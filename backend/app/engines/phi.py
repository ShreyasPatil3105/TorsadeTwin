# Phi evaluation + boundary calibration + monotonicity scan (§8).
# Phi(x) = qNet(x) - qNet_boundary; qNet_boundary = rho * qNet_ctrl (internal calibration, D1).
# Engines consume a PhiEvaluator callable so analytic surrogates can be used in tests (§26.3).
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

import numpy as np

from ..ep.simulate import EpEngine
from ..schemas.common import StateSpec
from ..services.errors import TorsadeTwinError


@dataclass(frozen=True)
class PhiEval:
    phi: float | None
    qnet: float | None
    credibility: str = "VERIFIED"
    tags: list[str] = field(default_factory=list)
    n_evals: int = 1


class PhiEvaluator(Protocol):
    def __call__(self, state: StateSpec) -> PhiEval: ...


class ModelPhiEvaluator:
    """Model-backed Phi evaluator: runs the EP engine and subtracts the calibrated boundary.

    Warm-start: caches the last converged physiological state and passes it as
    warm_state so subsequent Phi calls use SPEC n_warm=200 (not cold n_prepace=1000).
    Scientific settings unchanged; only state reuse per SPEC warm-start path.
    """

    def __init__(self, ep_engine: EpEngine, registry, rho: float, qnet_ctrl: float | None = None):
        self.ep_engine = ep_engine
        self.registry = registry
        self.rho = rho
        self._qnet_ctrl = qnet_ctrl
        self._last_state: list[float] | None = None

    @property
    def qnet_ctrl(self) -> float:
        if self._qnet_ctrl is None:
            self._qnet_ctrl = self._compute_control()
        return self._qnet_ctrl

    @property
    def qnet_boundary(self) -> float:
        return self.rho * self.qnet_ctrl

    def _compute_control(self) -> float:
        control = StateSpec(drugs=[], k_o_mM=5.4, cl_ms=2000)
        # Control is a cold start once; cache SS state for subsequent warm Phi calls.
        res = self.ep_engine.simulate(control, {}, return_trace=False)
        if res.qnet_C_per_F is None:
            raise TorsadeTwinError("E_NO_STEADY_STATE", "Control qNet unavailable.", http_status=422)
        if getattr(res, "state_vector", None) is not None:
            self._last_state = list(res.state_vector)
        return res.qnet_C_per_F

    def __call__(self, state: StateSpec) -> PhiEval:
        from ..ep.block import compute_block

        drugs = [(d.drug_id, d.exposure_multiplier * self.registry.get(d.drug_id).cmax_free_nM) for d in state.drugs]
        block = compute_block(self.registry, drugs)
        try:
            res = self.ep_engine.simulate(
                state, block.unblocked, return_trace=False, warm_state=self._last_state,
            )
        except TorsadeTwinError as exc:
            # A failed EP solve has no defensible Phi value. Margin and rescue
            # consume this explicit non-credible point instead of treating it
            # as a boundary crossing or silently substituting a number.
            return PhiEval(phi=None, qnet=None, credibility="UNKNOWN", tags=[exc.code], n_evals=1)
        if res.qnet_C_per_F is None:
            raise TorsadeTwinError("E_NO_STEADY_STATE", "qNet unavailable for state.", http_status=422)
        if res.converged and getattr(res, "state_vector", None) is not None:
            self._last_state = list(res.state_vector)
        return PhiEval(
            phi=res.qnet_C_per_F - self.qnet_boundary,
            qnet=res.qnet_C_per_F,
            credibility= "VERIFIED" if res.converged else "FAILED",
            tags=block.partial_panel,
            n_evals=1,
        )


def scan_monotonicity(phi: Callable[[StateSpec], PhiEval], space, axis_index: int,
                      n_scan: int, box_lo: np.ndarray, box_hi: np.ndarray,
                      evals: list | None = None) -> dict:
    """§8.5 monotonicity scan on one axis. Returns roots + monotonicity classification."""
    u0 = space.u0()
    lo = box_lo[axis_index]
    hi = box_hi[axis_index]
    grid = np.linspace(lo, hi, n_scan)
    vals: list[float | None] = []
    n_noncredible = 0
    for g in grid:
        u = u0.copy()
        u[axis_index] = g
        state = space.state_from_u(u)
        res = phi(state)
        if evals is not None:
            evals.append(res)
        if res.credibility != "VERIFIED" or res.phi is None:
            n_noncredible += 1
        vals.append(res.phi)
    # Only adjacent credible points can define a bracket or derivative. Unknown
    # values are retained as evidence that this scan is incomplete.
    sign_changes = 0
    derivatives: list[float] = []
    for i in range(len(grid) - 1):
        if vals[i] is not None and vals[i + 1] is not None:
            if np.sign(vals[i]) != np.sign(vals[i + 1]):
                sign_changes += 1
            derivatives.append(float(vals[i + 1] - vals[i]))
    deriv_sign_changes = sum(
        int(np.sign(derivatives[i]) != np.sign(derivatives[i + 1]))
        for i in range(len(derivatives) - 1)
    )
    roots = []
    brackets = []
    for i in range(len(grid) - 1):
        if vals[i] is None or vals[i + 1] is None:
            continue
        if vals[i] == 0.0:
            roots.append(float(grid[i]))
            brackets.append((float(grid[i]), float(grid[i])))
        elif vals[i] * vals[i + 1] < 0.0:
            roots.append(float((grid[i] + grid[i + 1]) / 2.0))
            brackets.append((float(grid[i]), float(grid[i + 1])))
    monotonic = "NON_MONOTONIC" if (sign_changes > 1 or deriv_sign_changes > 0) else "MONOTONIC"
    return {"roots": roots, "brackets": brackets, "monotonicity": monotonic,
            "sign_changes": sign_changes, "derivative_sign_changes": deriv_sign_changes,
            "n_noncredible": n_noncredible}
