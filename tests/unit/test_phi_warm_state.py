"""Prove ModelPhiEvaluator passes warm_state on the 2nd+ Phi evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.engines.phi import ModelPhiEvaluator
from backend.app.schemas.common import StateSpec, DrugExposure


@dataclass
class FakeSimResult:
    qnet_C_per_F: float = 0.1
    apd90_ms: float = 280.0
    converged: bool = True
    state_vector: list[float] = field(default_factory=lambda: [1.0, 2.0, 3.0])
    beats_run: int = 200
    convergence: dict = field(default_factory=dict)
    ra_flags: list = field(default_factory=list)
    v_rest_mV: float = -88.0
    v_peak_mV: float = 40.0
    dvdt_max_mV_per_ms: float = 200.0
    qnet_simpson_C_per_F: float = 0.1
    diagnostics: dict = field(default_factory=dict)


class RecordingEngine:
    """Minimal stand-in for EpEngine that records simulate() kwargs."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self._n = 0

    def simulate(self, state, block_unblocked, return_trace=False, warm_state=None):
        self._n += 1
        self.calls.append(
            {
                "n": self._n,
                "warm_state": None if warm_state is None else list(warm_state),
                "state_k": state.k_o_mM,
                "n_drugs": len(state.drugs),
            }
        )
        # Distinct state vectors per call so cache updates are visible
        return FakeSimResult(qnet_C_per_F=0.1 - 0.01 * self._n, state_vector=[float(self._n)] * 5)


class FakeRegistry:
    def get(self, drug_id: str):
        class Rec:
            cmax_free_nM = 2.0

            class Ch:
                channel = "IKr"
                ic50_nM = 10.0
                hill = 1.0
                runtime_excluded = False

            channels = [Ch()]

        return Rec()


def test_first_control_is_cold_and_second_phi_passes_warm_state():
    eng = RecordingEngine()
    phi = ModelPhiEvaluator(eng, FakeRegistry(), rho=0.75)

    # Control (property access) — must be cold
    q = phi.qnet_ctrl
    assert q is not None
    assert eng.calls[0]["warm_state"] is None, "control must be cold (warm_state=None)"

    # First explicit Phi after control — must receive cached control state
    st = StateSpec(
        k_o_mM=4.5,
        cl_ms=2000,
        drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)],
    )
    r1 = phi(st)
    assert r1.phi is not None
    assert eng.calls[1]["warm_state"] is not None, "2nd simulate must pass warm_state"
    assert eng.calls[1]["warm_state"] == [1.0] * 5  # state from control FakeSimResult

    # Third simulate (2nd Phi) — warm_state from previous Phi
    r2 = phi(st)
    assert eng.calls[2]["warm_state"] is not None
    assert eng.calls[2]["warm_state"] == [2.0] * 5


def test_failed_solve_does_not_overwrite_warm_cache():
    class FailThenOk(RecordingEngine):
        def simulate(self, state, block_unblocked, return_trace=False, warm_state=None):
            self._n += 1
            self.calls.append({"n": self._n, "warm_state": warm_state})
            if self._n == 2:
                from backend.app.services.errors import TorsadeTwinError

                raise TorsadeTwinError("E_NO_UPSTROKE", "fail", http_status=422)
            return FakeSimResult(state_vector=[float(self._n)] * 3)

    eng = FailThenOk()
    phi = ModelPhiEvaluator(eng, FakeRegistry(), rho=0.75)
    _ = phi.qnet_ctrl  # call 1 cold, cache [1,1,1]
    st = StateSpec(k_o_mM=4.5, cl_ms=2000, drugs=[])
    r = phi(st)  # call 2 fails
    assert r.credibility == "UNKNOWN"
    # cache still control state
    r2 = phi(st)  # call 3
    assert eng.calls[2]["warm_state"] == [1.0, 1.0, 1.0]
