from __future__ import annotations

import pytest

from backend.app.ep.block import combine_additive_occ, combine_indep_mult


def test_order_invariance():
    a = {"IKr": 0.5, "ICaL": 0.8}
    b = {"IKr": 0.6, "Ito": 0.9}
    f1 = combine_indep_mult([a, b])
    f2 = combine_indep_mult([b, a])
    assert f1 == f2


def test_multiplicative_vs_additive_differ():
    a = {"IKr": 0.4}
    b = {"IKr": 0.4}
    mult = combine_indep_mult([a, b])["IKr"]
    add = combine_additive_occ([a, b])["IKr"]
    assert mult != add


def test_single_drug_reduction():
    a = {"IKr": 0.5}
    assert combine_indep_mult([a])["IKr"] == 0.5


def test_additive_caps_at_zero_unblocked():
    a = {"IKr": 0.7}
    b = {"IKr": 0.7}
    assert combine_additive_occ([a, b])["IKr"] == 0.0  # min(1, 1.4) -> fully blocked
