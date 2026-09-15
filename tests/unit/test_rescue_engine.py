from __future__ import annotations

import math

from tests.conftest import make_state

from backend.app.engines.phi import PhiEval
from backend.app.engines.rescue import RescueEngine
from backend.app.schemas.common import DrugExposure, StateSpec


class _FakeRec:
    def __init__(self, discontinuable=False):
        self.discontinuable = discontinuable


class _FakeRegistry:
    def __init__(self, disc=None):
        self._disc = disc or {}

    def get(self, drug_id):
        return _FakeRec(self._disc.get(drug_id, False))


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


def _phi_linear(k0=4.0, m0=1.0):
    """Phi = (k - k0) + (log2(m) - log2(m0)); increasing k or m raises phi."""

    def _eval(state: StateSpec) -> PhiEval:
        k = state.k_o_mM
        m = state.drugs[0].exposure_multiplier if state.drugs else 1.0
        phi = (k - k0) + (math.log2(m + 1e-6) - math.log2(m0 + 1e-6))
        return PhiEval(phi=phi, qnet=phi + 0.075, credibility="VERIFIED")

    return _eval


def test_feasible_min_cost():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    # phi_target = 0.05 * qnet_ctrl = 0.05*0.075 = 0.00375
    # at k=4.0, phi=0 -> need phi >= 0.00375; cheapest: A1 to 4.2 (cost 0.2) gives phi 0.2
    res = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert res.status == "FEASIBLE"
    assert res.best_action.class_ == "A1_K_CORRECTION"
    assert res.best_action.param["k_o_mM"] == 4.2
    assert abs(res.best_action.cost - 0.2) < 1e-9


def test_full_table_returned():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    res = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert len(res.evaluated) == res.action_set_size


def test_deterministic_tie_order():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    r1 = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    r2 = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert [e.action.label() for e in r1.evaluated] == [e.action.label() for e in r2.evaluated]
