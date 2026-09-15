from __future__ import annotations

from backend.app.engines.rescue import Action, RescueEngine
from backend.app.schemas.common import DrugExposure, StateSpec


class _FakeRec:
    def __init__(self, discontinuable=False):
        self.discontinuable = discontinuable


class _FakeRegistry:
    def __init__(self, discontinuable_map=None):
        self._map = discontinuable_map or {}

    def get(self, drug_id):
        return _FakeRec(self._map.get(drug_id, False))


CFG = {
    "tau": 0.05,
    "action": {
        "k_correction_targets_mM": [3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4],
        "k_ceiling_mM": 5.4,
        "exposure_reduction_factors": [0.75, 0.5, 0.25],
        "max_action_set_size": 40,
    },
    "cost_weights": {"w_K": 1.0, "w_E": 1.0, "w_D": 6.0},
    "tol_cost": 1e-9,
    "tol_phi_borderline": 1e-4,
    "search_scope": "single_actions_only",
}


def test_action_set_size_formula():
    reg = _FakeRegistry({"dofetilide": False})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    actions = eng.build_action_set(x0)
    # |A| = 1 + |A1_permitted| + 3*D_present + |D_discontinuable|
    # A1 targets > 4.0 and <= 5.4: 4.2,4.4,4.6,4.8,5.0,5.2,5.4 = 7
    assert len(actions) == 1 + 7 + 3 * 1 + 0


def test_action_set_with_discontinuation():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    actions = eng.build_action_set(x0)
    assert len(actions) == 1 + 7 + 3 * 1 + 1
    assert any(a.class_ == "A3_DISCONTINUATION" for a in actions)


def test_action_set_deterministic_order():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    a1 = eng.build_action_set(x0)
    a2 = eng.build_action_set(x0)
    assert [x.label() for x in a1] == [x.label() for x in a2]


def test_upward_only_k_correction():
    reg = _FakeRegistry({})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[], k_o_mM=5.0)
    actions = eng.build_action_set(x0)
    k_targets = [a.param["k_o_mM"] for a in actions if a.class_ == "A1_K_CORRECTION"]
    assert all(t > 5.0 and t <= 5.4 for t in k_targets)
