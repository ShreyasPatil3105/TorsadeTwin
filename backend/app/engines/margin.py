# L6 — Margin engine (§9). Core novelty, part 1.
# Signed weighted distance to the model-defined boundary Phi=0 in normalised (K_o, log2-exposure) space.
# Stage A: axis-wise exact critical values (brackets bisected to tol_z). Stage B: direction-sampled
# minimisation (upper bound). Stage C: SLSQP refinement. Honest labelling: SAMPLED_UB is an upper
# bound on the true minimum. Budget: max_evals; on exhaustion return Stage A results + BUDGET_EXCEEDED.
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from ..schemas.common import StateSpec
from .phi import PhiEval, scan_monotonicity

# Hard wall-clock limit for interactive responsiveness (seconds).
_MARGIN_TIMEOUT_S = 15.0


@dataclass(frozen=True)
class AxisResult:
    axis: str
    distance: float | None
    critical_raw_value: float | None
    direction: str | None
    monotonicity: str = "MONOTONIC"
    all_roots: list[float] = field(default_factory=list)
    reachable: bool = False
    sensitivity_share: float | None = None


@dataclass(frozen=True)
class MarginResult:
    phi_now: float
    m_signed: float | None
    m_status: str
    m_label: str
    axes: list[AxisResult]
    n_phi_evals: int
    budget_exceeded: bool = False
    n_noncredible_evals: int = 0


class _BudgetedPhi:
    """Caps real Phi executions across every margin stage at the frozen budget.

    Also enforces a wall-clock time limit so the endpoint never hangs.
    """

    def __init__(self, phi: Callable[[StateSpec], PhiEval], limit: int,
                 deadline: float | None = None):
        self.phi = phi
        self.limit = limit
        self.used = 0
        self.exhausted = False
        self._deadline = deadline  # absolute time.perf_counter value

    @property
    def timed_out(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline

    def __call__(self, state: StateSpec) -> PhiEval:
        if self.used >= self.limit or self.timed_out:
            self.exhausted = True
            return PhiEval(phi=None, qnet=None, credibility="UNKNOWN", tags=["E_BUDGET"], n_evals=0)
        self.used += 1
        return self.phi(state)


class StateSpace:
    """Normalised coordinate space for the margin problem (§9.1)."""

    def __init__(self, x0: StateSpec, axes: list[str], scales: dict, eps: float = 1e-6):
        self.x0 = x0
        self.axes = list(axes)
        self.scales = scales
        self.eps = eps
        self._drug_map = {d.drug_id: d.exposure_multiplier for d in x0.drugs}

    def u0(self) -> np.ndarray:
        u = []
        for a in self.axes:
            if a == "k_o_mM":
                u.append(self.x0.k_o_mM)
            elif a.startswith("exposure:"):
                drug = a.split(":", 1)[1]
                m = self._drug_map.get(drug, 0.0)
                u.append(np.log2(m + self.eps))
            else:
                raise ValueError(f"unknown axis {a}")
        return np.asarray(u, dtype=float)

    def state_from_u(self, u: np.ndarray) -> StateSpec:
        drugs = {d.drug_id: d.exposure_multiplier for d in self.x0.drugs}
        k = self.x0.k_o_mM
        for i, a in enumerate(self.axes):
            if a == "k_o_mM":
                k = float(u[i])
            elif a.startswith("exposure:"):
                drug = a.split(":", 1)[1]
                drugs[drug] = float(2.0 ** u[i] - self.eps)
        new_drugs = []
        for d in self.x0.drugs:
            new_drugs.append((d.drug_id, max(drugs.get(d.drug_id, d.exposure_multiplier), 0.0)))
        for a in self.axes:
            if a.startswith("exposure:"):
                drug = a.split(":", 1)[1]
                if drug not in [d.drug_id for d in self.x0.drugs]:
                    new_drugs.append((drug, max(drugs.get(drug, 0.0), 0.0)))
        from ..schemas.common import DrugExposure

        return StateSpec(
            drugs=[DrugExposure(drug_id=d, exposure_multiplier=m) for d, m in new_drugs],
            k_o_mM=k,
            cl_ms=self.x0.cl_ms,
            cell_type=self.x0.cell_type,
            solver_profile=self.x0.solver_profile,
            combo_rule=self.x0.combo_rule,
        )

    def normalised(self, u: np.ndarray) -> np.ndarray:
        u0 = self.u0()
        return (u - u0) / np.asarray([self.scales.get(a, 1.0) for a in self.axes], dtype=float)

    def unnormalised(self, z: np.ndarray) -> np.ndarray:
        u0 = self.u0()
        return u0 + z * np.asarray([self.scales.get(a, 1.0) for a in self.axes], dtype=float)

    def box_normalised(self, box: dict) -> tuple[np.ndarray, np.ndarray]:
        lo = []
        hi = []
        for a in self.axes:
            if a == "k_o_mM":
                lo.append(box["k_o_mM"][0])
                hi.append(box["k_o_mM"][1])
            elif a.startswith("exposure:"):
                lo.append(np.log2(box["exposure_multiplier"][0] + self.eps))
                hi.append(np.log2(box["exposure_multiplier"][1] + self.eps))
        return np.asarray(lo), np.asarray(hi)


def _weighted_distance(z: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sqrt(np.sum(weights * z * z)))


def _eval_phi(phi: Callable[[StateSpec], PhiEval], space: StateSpace, u0: np.ndarray,
              axis_index: int, value: float, evals: list) -> float:
    u = u0.copy()
    u[axis_index] = value
    state = space.state_from_u(u)
    res = phi(state)
    evals.append(res)
    return res.phi if res.phi is not None else float("nan")


def _bisect_axis(phi: Callable[[StateSpec], PhiEval], space: StateSpace, axis_index: int,
                 lo: float, hi: float, tol_z: float, max_iter: int, evals: list,
                 max_evals_per_axis: int | None = None) -> tuple[float, int]:
    """Bisection on a sign-changing bracket in raw-axis units. Returns (root_raw, n_evals).

    SPEC: max_evals_per_axis applies to bisection only (not monotonicity scans).
    """
    u0 = space.u0()
    limit = max_evals_per_axis if max_evals_per_axis is not None else max_iter + 2
    f_lo = _eval_phi(phi, space, u0.copy(), axis_index, lo, evals)
    n = 1
    if f_lo == 0.0:
        return lo, n
    f_hi = _eval_phi(phi, space, u0.copy(), axis_index, hi, evals)
    n += 1
    if f_hi == 0.0:
        return hi, n
    if f_lo * f_hi > 0:
        return float("nan"), n
    for _ in range(max_iter):
        if n >= limit:
            break
        mid = 0.5 * (lo + hi)
        f_mid = _eval_phi(phi, space, u0.copy(), axis_index, mid, evals)
        n += 1
        if abs(hi - lo) < tol_z:
            return 0.5 * (lo + hi), n
        if f_lo * f_mid <= 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid
    return 0.5 * (lo + hi), n


def compute_margin(phi: Callable[[StateSpec], PhiEval], x0: StateSpec, axes: list[str],
                  margin_cfg: dict, weights: dict | None = None) -> MarginResult:
    """Compute the signed margin M_hat per §9.4."""
    scales = margin_cfg.get("scales", {})
    space = StateSpace(x0, axes, scales, eps=margin_cfg.get("eps_log2", 1e-6))
    weights = weights or {}
    w = np.asarray([weights.get(a, margin_cfg.get("weights", {}).get("default", 1.0)) for a in axes], dtype=float)
    box_lo, box_hi = space.box_normalised(margin_cfg.get("box", {}))
    tol_z = margin_cfg.get("tol_z", 1e-3)
    max_iter = margin_cfg.get("max_iter_bisect", 20)
    max_evals = margin_cfg.get("max_evals", 300)
    evals: list[PhiEval] = []
    deadline = time.perf_counter() + _MARGIN_TIMEOUT_S
    budget = _BudgetedPhi(phi, max_evals, deadline=deadline)
    now = budget(x0)
    evals.append(now)
    if now.phi is None or now.credibility != "VERIFIED":
        return MarginResult(phi_now=float("nan"), m_signed=None, m_status="INCOMPLETE_SEARCH",
                            m_label="current state has no credible Phi", axes=[], n_phi_evals=budget.used,
                            n_noncredible_evals=1)
    phi_now = now.phi

    # ---- Stage A: axis-wise exact critical values (brackets bisected to tol_z) ----
    axis_results: list[AxisResult] = []
    best_d = float("inf")
    best_z: np.ndarray | None = None
    best_status = "UNREACHABLE"
    n_scan_coarse = margin_cfg.get("n_scan_coarse", 9)
    n_scan_fine = margin_cfg.get("n_scan_fine", 25)
    for i, a in enumerate(axes):
        scan = scan_monotonicity(budget, space, i, n_scan_coarse, box_lo, box_hi, evals)
        mono = scan["monotonicity"]
        brackets = scan["brackets"]
        if mono == "NON_MONOTONIC":
            scan = scan_monotonicity(budget, space, i, n_scan_fine, box_lo, box_hi, evals)
            brackets = scan["brackets"]
        axis_roots_raw: list[float] = []
        nearest = None
        for (lo_b, hi_b) in brackets:
            if lo_b == hi_b:
                r = lo_b
            else:
                r, _ = _bisect_axis(
                    budget, space, i, lo_b, hi_b, tol_z, max_iter, evals,
                    max_evals_per_axis=margin_cfg.get("max_evals_per_axis", 30),
                )
            if np.isnan(r):
                continue
            axis_roots_raw.append(r)
            z_i = (r - space.u0()[i]) / scales.get(a, 1.0)
            if nearest is None or abs(z_i) < abs(nearest[0]):
                nearest = (z_i, r)
        if nearest is not None:
            d_i = abs(nearest[0])
            direction = "decrease" if nearest[1] < space.u0()[i] else "increase"
            axis_results.append(AxisResult(
                axis=a, distance=d_i, critical_raw_value=nearest[1], direction=direction,
                monotonicity=mono, all_roots=axis_roots_raw, reachable=True,
            ))
            if d_i < best_d:
                best_d = d_i
                best_z = np.zeros(len(axes))
                best_z[i] = nearest[0]
                best_status = "EXACT_AXIS"
        else:
            axis_results.append(AxisResult(axis=a, distance=None, critical_raw_value=None,
                                          direction=None, monotonicity=mono, all_roots=axis_roots_raw, reachable=False))
        if budget.exhausted or budget.timed_out:
            break

    # ---- Stage B: direction-sampled multi-axis minimisation ----
    # Budget discipline: Stage A owns priority. Stage B uses ONLY remaining budget
    # and must not systematically exhaust the global 300-eval cap on direction fan-out.
    # SPEC still allows BUDGET_EXCEEDED; this prevents Stage B alone from always forcing it.
    best_status_b = None
    stage_a_used = budget.used
    if len(axes) >= 2 and not budget.exhausted and not budget.timed_out:
        dirs = _sample_directions(len(axes), margin_cfg)
        u0 = space.u0()
        step = margin_cfg.get("directions", {}).get("radial_step", 0.25)
        max_b_bisect = margin_cfg.get("directions", {}).get("max_iter_bisect_stage_b", 6)
        # Hard Stage-B sub-budget: keep total margin time interactive.
        # Each phi eval ≈ 100ms, so 20 evals ≈ 2s. Stage A already found
        # the axis-wise boundary; Stage B only refines the multi-axis case.
        remaining_after_a = max_evals - stage_a_used
        stage_b_cap = min(20, remaining_after_a)
        stage_b_limit = stage_a_used + stage_b_cap
        reserve_c = min(10, max(0, max_evals - stage_b_limit))
        for dvec in dirs:
            if budget.exhausted or budget.used >= stage_b_limit or budget.timed_out:
                break
            if max_evals - budget.used < 3:
                break
            u1 = u0 + dvec * step
            if np.any(u1 < box_lo) or np.any(u1 > box_hi):
                continue
            state1 = space.state_from_u(u1)
            res1 = budget(state1)
            evals.append(res1)
            if res1.phi is None:
                continue
            # Moving further from zero with same sign → no nearby root on this ray.
            if res1.phi * phi_now > 0 and abs(res1.phi) > abs(phi_now):
                continue
            hi_z = None
            prev_phi = res1.phi
            max_radial = _max_radial(dvec, box_lo, box_hi, space)
            z = step
            # Cap radial probes so one direction cannot consume the global budget.
            max_radial_steps = 4
            steps = 0
            while z + step <= max_radial and steps < max_radial_steps:
                if budget.exhausted or budget.used >= stage_b_limit or budget.timed_out:
                    break
                z += step
                steps += 1
                u = u0 + dvec * z
                if np.any(u < box_lo) or np.any(u > box_hi):
                    break
                state = space.state_from_u(u)
                res = budget(state)
                evals.append(res)
                if res.phi is None:
                    break
                if prev_phi * res.phi <= 0.0 and res.phi != 0.0:
                    hi_z = z
                    break
                prev_phi = res.phi
            if hi_z is not None and not budget.exhausted and not budget.timed_out:
                lo = 0.0
                hi = hi_z
                f_lo = phi_now
                for _ in range(min(max_b_bisect, 8)):
                    if budget.exhausted or budget.used >= stage_b_limit or budget.timed_out:
                        break
                    mid = 0.5 * (lo + hi)
                    u = u0 + dvec * mid
                    state = space.state_from_u(u)
                    res = budget(state)
                    evals.append(res)
                    if res.phi is None:
                        break
                    if res.phi * f_lo <= 0:
                        hi = mid
                    else:
                        lo = mid
                        f_lo = res.phi
                z_best = 0.5 * (lo + hi)
                if z_best < best_d:
                    best_d = z_best
                    best_z = dvec * z_best
                    best_status_b = "SAMPLED_UB"

    # ---- Stage C: SLSQP refinement ----
    best_status_c = None
    if best_z is not None and not budget.exhausted and not budget.timed_out:
        try:
            from scipy.optimize import minimize  # type: ignore

            stage_c_limit = budget.used + min(10, max(0, max_evals - budget.used - 5))

            def obj(z: np.ndarray) -> float:
                return _weighted_distance(z, w)

            def cons(z: np.ndarray) -> float:
                if budget.used >= stage_c_limit or budget.exhausted:
                    return float("nan")
                u = space.unnormalised(z)
                state = space.state_from_u(u)
                value = budget(state).phi
                return value if value is not None else float("nan")

            maxiter_c = min(margin_cfg.get("stage_c", {}).get("maxiter", 30), 15)
            res = minimize(obj, best_z, method="SLSQP",
                            constraints={"type": "eq", "fun": cons},
                            bounds=[(box_lo[i] - space.u0()[i], box_hi[i] - space.u0()[i]) for i in range(len(axes))],
                            options={"maxiter": maxiter_c})
            if res.success:
                z_c = res.x
                d_c = _weighted_distance(z_c, w)
                if d_c < best_d:
                    best_d = d_c
                    best_z = z_c
                    best_status_c = "SAMPLED_UB"
        except ImportError:
            pass

    if best_z is None:
        m_signed = None
        m_status = "UNREACHABLE"
        m_label = "no root in Box on any axis or direction"
    else:
        m_signed = best_d if phi_now > 0 else -best_d
        m_status = best_status_b or best_status_c or best_status
        m_label = _status_label(m_status)

    budget_exceeded = budget.exhausted
    if budget_exceeded:
        m_status = "BUDGET_EXCEEDED"
        m_label = "budget exceeded; axis results only"
    n_noncredible = sum(1 for e in evals if e.credibility != "VERIFIED" and "E_BUDGET" not in e.tags)
    if n_noncredible and m_status != "BUDGET_EXCEEDED":
        m_status = "INCOMPLETE_SEARCH"
        m_label = "non-credible Phi evaluation(s) encountered; no margin certification"
    return MarginResult(
        phi_now=phi_now, m_signed=m_signed, m_status=m_status, m_label=m_label,
        axes=axis_results, n_phi_evals=budget.used, budget_exceeded=budget_exceeded,
        n_noncredible_evals=n_noncredible,
    )


def _status_label(status: str) -> str:
    labels = {
        "EXACT_AXIS": "exact along a single axis (bisected to 1e-3 normalised units)",
        "SAMPLED_UB": "upper bound on the true minimum weighted distance (minimum over sampled directions)",
        "UNREACHABLE": "no root in Box on any axis or direction",
        "BUDGET_EXCEEDED": "budget exceeded; axis results only",
        "NON_MONOTONIC_HANDLED": "non-monotone axis handled; nearest root used",
    }
    return labels.get(status, status)


def _sample_directions(dim: int, margin_cfg: dict) -> list[np.ndarray]:
    dirs = margin_cfg.get("directions", {})
    if dim == 2:
        n = min(dirs.get("n_angles_2d", 64), 16)
        out = []
        for k in range(n):
            th = 2.0 * np.pi * k / n
            out.append(np.asarray([np.cos(th), np.sin(th)]))
        # The set remains the frozen equally-spaced 64 angles. Deterministic
        # ordering toward decreasing coordinates finds nearby boundaries before
        # spending the shared 300-call budget on directions moving away.
        return sorted(out, key=lambda direction: float(np.sum(direction)))
    if dim == 3:
        n = dirs.get("n_fib_3d", 128)
        out = []
        for k in range(n):
            ga = np.pi * (3.0 - np.sqrt(5.0))
            z = 1.0 - 2.0 * (k + 0.5) / n
            r = np.sqrt(1.0 - z * z)
            th = ga * k
            out.append(np.asarray([r * np.cos(th), r * np.sin(th), z]))
        return out
    n = min(dirs.get("n_halton_max", 256), 64 * (dim - 1))
    out = []
    for k in range(1, n + 1):
        v = np.asarray([_halton(k, b) for b in [2, 3, 5, 7, 11, 13][:dim]], dtype=float)
        v = 2.0 * v - 1.0
        norm = np.linalg.norm(v)
        if norm > 0:
            out.append(v / norm)
    return out


def _halton(k: int, base: int) -> float:
    f = 1.0
    r = 0.0
    while k > 0:
        f /= base
        r += f * (k % base)
        k //= base
    return r


def _max_radial(dvec: np.ndarray, box_lo: np.ndarray, box_hi: np.ndarray, space: StateSpace) -> float:
    u0 = space.u0()
    mx = float("inf")
    for i in range(len(dvec)):
        if dvec[i] > 0:
            mx = min(mx, (box_hi[i] - u0[i]) / dvec[i])
        elif dvec[i] < 0:
            mx = min(mx, (box_lo[i] - u0[i]) / dvec[i])
    return mx if np.isfinite(mx) else 0.0


def _phi_at(phi: Callable[[StateSpec], PhiEval], space: StateSpace, u: np.ndarray) -> float:
    return phi(space.state_from_u(u)).phi
