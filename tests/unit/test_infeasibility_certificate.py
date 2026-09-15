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


def _phi_flat_negative():
    """Phi stays below the target for every action (severe scenario)."""

    def _eval(state: StateSpec) -> PhiEval:
        return PhiEval(phi=-0.002, qnet=0.073, credibility="VERIFIED")

    return _eval


def test_exhaustive_infeasibility():
    reg = _FakeRegistry()
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    res = eng.run(_phi_flat_negative(), x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert res.status == "INFEASIBLE_EXHAUSTIVE"
    assert len(res.evaluated) == res.action_set_size
    assert res.infeasibility is not None
    assert res.infeasibility.closest_action is not None


def test_downgrade_on_noncredible():
    calls = {"n": 0}

    def _phi_mixed(state: StateSpec) -> PhiEval:
        calls["n"] += 1
        cred = "VERIFIED" if calls["n"] != 3 else "UNVERIFIED"
        return PhiEval(phi=-0.002, qnet=0.073, credibility=cred)

    reg = _FakeRegistry()
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    res = eng.run(_phi_mixed, x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert res.status == "INCOMPLETE_SEARCH"
    assert res.n_noncredible >= 1


def test_no_solution_found_on_borderline():
    def _phi_borderline(state: StateSpec) -> PhiEval:
        # phi within tol_phi of the target for every action
        return PhiEval(phi=0.0037, qnet=0.0787, credibility="VERIFIED")

    reg = _FakeRegistry()
    eng = RescueEngine(CFG, reg)
    x0 = StateSpec(drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)], k_o_mM=4.0)
    res = eng.run(_phi_borderline, x0, tau=0.05, qnet_ctrl=0.075, margin_cfg=None)
    assert res.status == "NO_SOLUTION_FOUND"
