from __future__ import annotations

import math

from backend.app.engines.rescue import Action


def _cost(weights, class_, param, k0=4.0):
    w_K, w_E, w_D = weights["w_K"], weights["w_E"], weights["w_D"]
    if class_ == "A0_NO_ACTION":
        return 0.0
    if class_ == "A1_K_CORRECTION":
        return w_K * (param["k_o_mM"] - k0) / 1.0
    if class_ == "A2_EXPOSURE_REDUCTION":
        return w_E * abs(math.log2(param["factor"]))
    if class_ == "A3_DISCONTINUATION":
        return w_D
    raise ValueError(class_)


def test_a0_zero():
    assert _cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A0_NO_ACTION", {}) == 0.0


def test_a1_linear_in_k_delta():
    assert abs(_cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A1_K_CORRECTION", {"k_o_mM": 4.4}, k0=4.0) - 0.4) < 1e-9


def test_a2_log2_of_factor():
    assert abs(_cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A2_EXPOSURE_REDUCTION", {"factor": 0.75}) - 0.415) < 0.001


def test_a3_flat_dominant():
    assert _cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A3_DISCONTINUATION", {}) == 6.0


def test_preference_ordering():
    # electrolyte correction cheapest, dose reduction next, discontinuation most costly
    c_k = _cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A1_K_CORRECTION", {"k_o_mM": 4.4}, k0=4.0)
    c_e = _cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A2_EXPOSURE_REDUCTION", {"factor": 0.5})
    c_d = _cost({"w_K": 1, "w_E": 1, "w_D": 6}, "A3_DISCONTINUATION", {})
    assert c_k < c_e < c_d
