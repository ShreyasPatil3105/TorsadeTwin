from __future__ import annotations

from tests.unit.test_rescue_engine import CFG, _FakeRegistry, _phi_linear

from backend.app.engines.rescue import RescueEngine
from backend.app.schemas.common import DrugExposure, StateSpec


def test_rescue_determinism():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    r1 = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    r2 = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert r1.status == r2.status
    assert [e.action.label() for e in r1.evaluated] == [e.action.label() for e in r2.evaluated]
    assert r1.best_action == r2.best_action
