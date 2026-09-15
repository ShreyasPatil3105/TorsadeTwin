from __future__ import annotations

import math

from backend.app.ep.block import (
    combine_additive_occ,
    combine_indep_mult,
    hill_block_fraction,
    hill_unblocked_fraction,
)


def test_b_half_at_ic50_for_h1():
    b = hill_block_fraction(100.0, 100.0, 1.0)
    assert abs(b - 0.5) < 1e-12


def test_monotone_in_concentration():
    f1 = hill_unblocked_fraction(10.0, 100.0, 1.0)
    f2 = hill_unblocked_fraction(50.0, 100.0, 1.0)
    f3 = hill_unblocked_fraction(200.0, 100.0, 1.0)
    assert f1 > f2 > f3
    assert f1 > 0 and f3 > 0


def test_f_in_open_unit_interval():
    for c in [0.1, 1.0, 10.0, 100.0, 1000.0]:
        f = hill_unblocked_fraction(c, 100.0, 1.0)
        assert 0.0 < f <= 1.0


def test_h_sensitivity():
    # higher hill -> steeper block at C > IC50
    f_lo = hill_unblocked_fraction(200.0, 100.0, 1.0)
    f_hi = hill_unblocked_fraction(200.0, 100.0, 2.0)
    assert f_hi < f_lo


def test_zero_concentration_no_block():
    assert hill_unblocked_fraction(0.0, 100.0, 1.0) == 1.0


def test_multiplicative_combination():
    a = {"IKr": 0.5, "ICaL": 1.0}
    b = {"IKr": 0.5, "ICaL": 0.8}
    F = combine_indep_mult([a, b])
    assert abs(F["IKr"] - 0.25) < 1e-12
    assert abs(F["ICaL"] - 0.8) < 1e-12


def test_additive_occupancy():
    a = {"IKr": 0.4}
    b = {"IKr": 0.4}
    F = combine_additive_occ([a, b])
    assert abs(F["IKr"] - 0.2) < 1e-12


def test_single_drug_reduces_to_hill():
    a = {"IKr": 0.6}
    assert abs(combine_indep_mult([a])["IKr"] - 0.6) < 1e-12
