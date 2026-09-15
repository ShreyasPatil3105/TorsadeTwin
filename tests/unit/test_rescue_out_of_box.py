from __future__ import annotations

import math

from tests.unit.test_rescue_engine import CFG, _FakeRegistry

from backend.app.engines.phi import PhiEval
from backend.app.engines.rescue import RescueEngine
from backend.app.schemas.common import DrugExposure, StateSpec


class _FakeRec:
    discontinuable = False


class _FakeRegistry:
    def get(self, drug_id):
        return _FakeRec()


def _phi_linear():
    def _eval(state: StateSpec) -> PhiEval:
        k = state.k_o_mM
        m = state.drugs[0].exposure_multiplier if state.drugs else 1.0
        phi = (k - 4.0) + (math.log2(m + 1e-6) - math.log2(1.0 + 1e-6))
        return PhiEval(phi=phi, qnet=phi + 0.075, credibility="VERIFIED")

    return _eval


def test_actions_within_box_only():
    reg = _FakeRegistry()
    eng = RescueEngine(CFG, reg)
    # k at ceiling 5.4 -> no A1 actions permitted (upward only, <= 5.4)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=5.4)
    actions = eng.build_action_set(x0)
    assert not any(a.class_ == "A1_K_CORRECTION" for a in actions)
