# L7 — Binding constraint identification (§10).
# The binding axis is the one with the smallest normalised distance to the boundary (computed, never eyeballed).
# Local sensitivity share is reported separately as "local influence" only.
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from ..schemas.common import StateSpec
from .margin import AxisResult, MarginResult, StateSpace
from .phi import PhiEval

TOL_TIE = 0.05


@dataclass(frozen=True)
class BindingResult:
    binding_axis: str | None
    d_binding: float | None
    critical_value: float | None
    direction: str | None
    tied_axes: list[str] = field(default_factory=list)
    sensitivity_share: dict[str, float] = field(default_factory=dict)
    alternative_axis: str | None = None
    alternative_critical_value: float | None = None
    unreachable_axes: list[str] = field(default_factory=list)
    monotonicity: dict[str, str] = field(default_factory=dict)
    distance_vs_sensitivity_disagree: bool = False
    status: str = "OK"
    n_phi_evals: int = 0


def compute_binding_constraint(phi: Callable[[StateSpec], PhiEval], x0: StateSpec, axes: list[str],
                               margin_cfg: dict, margin_result: MarginResult | None = None) -> BindingResult:
    """§10.2. Reuses Stage A axis results from the margin call when provided."""
    supplied_margin = margin_result is not None and bool(margin_result.axes)
    if supplied_margin:
        axis_results = margin_result.axes
    else:
        from .margin import compute_margin

        margin_result = compute_margin(phi, x0, axes, margin_cfg)
        axis_results = margin_result.axes

    scales = margin_cfg.get("scales", {})
    space = StateSpace(x0, axes, scales, eps=margin_cfg.get("eps_log2", 1e-6))

    reachable = [(a, r) for a, r in zip(axes, axis_results) if r.reachable and r.distance is not None]
    unreachable = [a for a, r in zip(axes, axis_results) if not r.reachable]
    if not reachable:
        return BindingResult(binding_axis=None, d_binding=None, critical_value=None, direction=None,
                             unreachable_axes=unreachable, status="NO_REACHABLE_BOUNDARY_IN_BOX")

    # distance-based winner
    d_values = [(a, r.distance) for a, r in reachable]
    d_min = min(d for _, d in d_values)
    tied = [a for a, d in d_values if abs(d - d_min) <= TOL_TIE]

    # local sensitivity share: g_i = dPhi/dz_i by central finite difference, h = 0.05.
    # The global 300-Phi budget includes these binding finite differences. When a
    # margin result is supplied, only the unused portion of that same budget may
    # be consumed here; exhausted budgets produce UNKNOWN sensitivity rather than
    # silently exceeding the frozen cap.
    h = 0.05
    u0 = space.u0()
    grads: dict[str, float] = {}
    remaining = int(margin_cfg.get("max_evals", 300))
    if supplied_margin:
        remaining = max(0, remaining - int(margin_result.n_phi_evals))

    class _RemainingBudget:
        def __init__(self, fn, limit):
            self.fn, self.limit, self.used = fn, limit, 0
        def __call__(self, state):
            from .phi import PhiEval
            if self.used >= self.limit:
                return PhiEval(phi=None, qnet=None, credibility="UNKNOWN", tags=["E_BUDGET"], n_evals=0)
            self.used += 1
            return self.fn(state)

    bphi = _RemainingBudget(phi, remaining)
    for i, a in enumerate(axes):
        up = u0.copy(); up[i] += h * scales.get(a, 1.0)
        dn = u0.copy(); dn[i] -= h * scales.get(a, 1.0)
        rp = bphi(space.state_from_u(up)); rm = bphi(space.state_from_u(dn))
        if rp.phi is None or rm.phi is None:
            grads[a] = float("nan")
        else:
            grads[a] = (rp.phi - rm.phi) / (2.0 * h)
    credible_grads = {a:g for a,g in grads.items() if np.isfinite(g)}
    total = sum(abs(g) for g in credible_grads.values())
    share = {a: (abs(credible_grads[a]) / total if a in credible_grads and total > 0 else 0.0) for a in axes}

    # order tied axes by |dPhi/dz_i| descending
    tied_sorted = sorted(tied, key=lambda a: -abs(grads.get(a, float("-inf"))))
    binding_axis = tied_sorted[0]
    binding_res = next(r for a, r in zip(axes, axis_results) if a == binding_axis)

    # alternative dimension = second smallest distance
    others = sorted([(a, d) for a, d in d_values if a != binding_axis], key=lambda x: x[1])
    alt_axis = others[0][0] if others else None
    alt_critical = next((r.critical_raw_value for a, r in zip(axes, axis_results) if a == alt_axis), None)

    # disagreement badge
    top_sens = max(share, key=lambda a: share[a]) if share else binding_axis
    disagree = top_sens != binding_axis if credible_grads else False

    return BindingResult(
        binding_axis=binding_axis,
        d_binding=d_min,
        critical_value=binding_res.critical_raw_value,
        direction=binding_res.direction,
        tied_axes=tied_sorted[1:],
        sensitivity_share={a: round(100.0 * s, 2) for a, s in share.items()},
        alternative_axis=alt_axis,
        alternative_critical_value=alt_critical,
        unreachable_axes=unreachable,
        monotonicity={a: r.monotonicity for a, r in zip(axes, axis_results)},
        distance_vs_sensitivity_disagree=disagree,
        status="BUDGET_EXHAUSTED" if len(credible_grads) < len(axes) else "OK",
        n_phi_evals=bphi.used,
    )
