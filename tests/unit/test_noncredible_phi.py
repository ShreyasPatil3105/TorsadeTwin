from __future__ import annotations

from backend.app.engines.margin import compute_margin
from backend.app.engines.phi import PhiEval
from tests.conftest import make_state, margin_cfg


def test_noncredible_scan_point_does_not_become_a_boundary_or_exceed_budget():
    calls = 0

    def phi(state):
        nonlocal calls
        calls += 1
        if state.k_o_mM <= 3.1:
            return PhiEval(phi=None, qnet=None, credibility="UNKNOWN", tags=["E_NO_UPSTROKE"])
        value = state.k_o_mM - 3.2
        return PhiEval(phi=value, qnet=value + 0.1)

    cfg = margin_cfg()
    cfg["max_evals"] = 20
    result = compute_margin(phi, make_state(k_o_mM=4.0), ["k_o_mM"], cfg)
    assert result.m_status == "INCOMPLETE_SEARCH"
    assert result.n_noncredible_evals > 0
    assert result.n_phi_evals == calls
    assert result.n_phi_evals <= 20
