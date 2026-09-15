from __future__ import annotations

import math

from tests.unit.test_rescue_engine import CFG, _FakeRegistry

from backend.app.engines.phi import PhiEval
from backend.app.engines.rescue import RescueEngine
from backend.app.schemas.common import DrugExposure, StateSpec


class _FakeRec:
    discontinuable = True


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


def test_post_margin_ge_target():
    reg = _FakeRegistry()
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    res = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, compute_post_margin=False, margin_cfg=None)
    assert res.status == "FEASIBLE"
    # post-rescue phi must be >= target
    assert res.post_phi is not None and res.post_phi >= res.phi_target
