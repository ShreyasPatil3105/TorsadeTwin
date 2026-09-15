from __future__ import annotations

import math

from tests.conftest import analytic_phi_plane, make_state, margin_cfg

from backend.app.engines.binding import compute_binding_constraint


def test_binding_is_distance_winner():
    # k root at 3.5 (distance 0.5); m root at m=0.5 (distance 1.0) -> k is binding
    phi = analytic_phi_plane(intercept=1.0, k_slope=2.0, m_slope=1.0)
    x0 = make_state(k_o_mM=4.0, m=1.0)
    b = compute_binding_constraint(phi, x0, ["k_o_mM", "exposure:dofetilide"], margin_cfg())
    assert b.binding_axis == "k_o_mM"
    assert b.critical_value is not None and abs(b.critical_value - 3.5) < 0.1
    assert b.alternative_axis == "exposure:dofetilide"


def test_unreachable_axes_reported():
    # m slope 0 -> no root along exposure axis within box
    phi = analytic_phi_plane(intercept=1.0, k_slope=1.0, m_slope=0.0)
    x0 = make_state(k_o_mM=4.0, m=1.0)
    b = compute_binding_constraint(phi, x0, ["k_o_mM", "exposure:dofetilide"], margin_cfg())
    assert "exposure:dofetilide" in b.unreachable_axes


def test_all_unreachable_status():
    # constant positive phi -> no root anywhere
    def _const(state):
        from backend.app.engines.phi import PhiEval

        return PhiEval(phi=1.0, qnet=1.075, credibility="VERIFIED")

    x0 = make_state(k_o_mM=4.0, m=1.0)
    b = compute_binding_constraint(_const, x0, ["k_o_mM", "exposure:dofetilide"], margin_cfg())
    assert b.binding_axis is None
    assert b.status == "NO_REACHABLE_BOUNDARY_IN_BOX"


def test_disagreement_badge():
    # For a locally-linear Phi, the distance winner and the sensitivity winner always coincide
    # (distance_i ~ |phi0|/|slope_i|). The disagreement case therefore requires a NON-LINEAR
    # Phi: steep local slope in m (high sensitivity) but no m boundary inside the box (so m is
    # not the distance winner). k is the only reachable axis -> distance winner is k.
    def _phi(state):
        from backend.app.engines.phi import PhiEval

        k = state.k_o_mM
        m = state.drugs[0].exposure_multiplier if state.drugs else 1.0
        u_m = math.log2(m + 1e-6)
        # 10*(k-3.5): k root at 3.5 (distance 0.5). 1.5*tanh(10*u_m): steep at m=1
        # (sensitivity ~15) but bounded in [-1.5, 1.5], so phi_m stays positive in the box.
        phi = 10.0 * (k - 3.5) + 1.5 * math.tanh(10.0 * u_m)
        return PhiEval(phi=phi, qnet=phi + 0.075, credibility="VERIFIED")

    x0 = make_state(k_o_mM=4.0, m=1.0)
    b = compute_binding_constraint(_phi, x0, ["k_o_mM", "exposure:dofetilide"], margin_cfg())
    # distance winner is k (the only reachable axis); sensitivity winner is m (steep) -> disagree
    assert b.binding_axis == "k_o_mM"
    assert "exposure:dofetilide" in b.unreachable_axes
    assert b.distance_vs_sensitivity_disagree is True
