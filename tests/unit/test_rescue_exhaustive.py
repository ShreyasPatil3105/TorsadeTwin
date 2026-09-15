from __future__ import annotations

from tests.unit.test_rescue_engine import CFG, _FakeRegistry, _phi_linear

from backend.app.engines.rescue import RescueEngine
from backend.app.schemas.common import DrugExposure, StateSpec


def test_every_action_evaluated():
    reg = _FakeRegistry({"dofetilide": True})
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    res = eng.run(_phi_linear(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    # count check against |A|
    assert len(res.evaluated) == res.action_set_size
    assert res.action_set_size == 1 + 7 + 3 * 1 + 1
