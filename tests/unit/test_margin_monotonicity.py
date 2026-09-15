from __future__ import annotations

from tests.conftest import analytic_phi_nonmonotone, make_state, margin_cfg

from backend.app.engines.margin import compute_margin


def test_nonmonotone_two_roots_reported():
    # Phi = (k-3.0)*(k-4.5); roots at k=3.0 and k=4.5. Start at k=4.0.
    phi = analytic_phi_nonmonotone()
    x0 = make_state(k_o_mM=4.0, m=1.0)
    mr = compute_margin(phi, x0, ["k_o_mM"], margin_cfg())
    # nearest root is 4.5 -> distance 0.5
    assert mr.m_signed is not None and abs(abs(mr.m_signed) - 0.5) < 1e-2
    axis = mr.axes[0]
    assert axis.monotonicity == "NON_MONOTONIC"
    assert len(axis.all_roots) >= 2
