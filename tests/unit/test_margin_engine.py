from __future__ import annotations

from tests.conftest import analytic_phi_paraboloid, analytic_phi_plane, make_state, margin_cfg

from backend.app.engines.margin import compute_margin


def test_plane_distance_recovered():
    # Phi = 1.0 + (k-4.0) + (log2(m)-log2(1))  -> boundary at k = 3.0 (m=1)
    # distance from k=4.0 to k=3.0 along the k axis = 1.0 normalised unit
    phi = analytic_phi_plane(intercept=1.0, k_slope=1.0, m_slope=0.0)
    x0 = make_state(k_o_mM=4.0, m=1.0)
    mr = compute_margin(phi, x0, ["k_o_mM"], margin_cfg())
    assert mr.m_status == "EXACT_AXIS"
    assert mr.m_signed is not None and abs(mr.m_signed - 1.0) < 1e-2


def test_plane_two_axis_distance():
    # Phi = 1.0 + (k-4.0) + (log2(m)-log2(1)) is a plane in normalised space; the true
    # minimum weighted distance from the origin to the plane 1.0 + z_k + z_m = 0 is the
    # perpendicular distance |1.0|/sqrt(1^2+1^2) = 1/sqrt(2) (Stage B direction sampling).
    import math

    phi = analytic_phi_plane(intercept=1.0, k_slope=1.0, m_slope=1.0)
    x0 = make_state(k_o_mM=4.0, m=1.0)
    mr = compute_margin(phi, x0, ["k_o_mM", "exposure:dofetilide"], margin_cfg())
    assert mr.m_signed is not None and abs(mr.m_signed - 1.0 / math.sqrt(2.0)) < 0.02


def test_paraboloid_distance():
    # circle radius 0.5 centred at (3.5, log2(2)); start at (4.0, 1.0)
    # distance from (4.0, 0.0) to circle centred (3.5, 1.0) radius 0.5
    import math

    phi = analytic_phi_paraboloid(center_k=3.5, center_m=2.0, radius=0.5)
    x0 = make_state(k_o_mM=4.0, m=1.0)
    mr = compute_margin(phi, x0, ["k_o_mM", "exposure:dofetilide"], margin_cfg())
    center = (3.5, math.log2(2.0))
    start = (4.0, math.log2(1.0))
    dist = math.sqrt((start[0] - center[0]) ** 2 + (start[1] - center[1]) ** 2) - 0.5
    assert mr.m_signed is not None and abs(mr.m_signed - dist) < 1e-2


def test_safe_side_positive_unsafe_negative():
    phi = analytic_phi_plane(intercept=1.0, k_slope=1.0, m_slope=0.0)
    safe = compute_margin(phi, make_state(k_o_mM=4.0), ["k_o_mM"], margin_cfg())
    assert safe.m_signed > 0
    unsafe = compute_margin(phi, make_state(k_o_mM=2.5), ["k_o_mM"], margin_cfg())
    assert unsafe.m_signed is not None and unsafe.m_signed < 0
