from __future__ import annotations

from tests.conftest import analytic_phi_plane, make_state, margin_cfg

from backend.app.engines.margin import compute_margin


def test_budget_exhaustion_returns_status_not_silent_number():
    cfg = margin_cfg()
    cfg["max_evals"] = 5  # tiny budget
    phi = analytic_phi_plane(intercept=1.0, k_slope=1.0, m_slope=0.0)
    x0 = make_state(k_o_mM=4.0, m=1.0)
    mr = compute_margin(phi, x0, ["k_o_mM"], cfg)
    assert mr.budget_exceeded is True
    assert mr.m_status == "BUDGET_EXCEEDED"
