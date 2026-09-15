from __future__ import annotations

import math

from tests.conftest import make_state, margin_cfg

from backend.app.data.scores import TisdaleBand, TisdaleItem, TisdaleScore
from backend.app.engines.blindspot import run_blindspot
from backend.app.engines.phi import PhiEval
from backend.app.schemas.common import DrugExposure, StateSpec


def _score():
    items = [
        TisdaleItem(id="serum_k_le_3_5", type="threshold", points=2, variable="k_o_mM", operator="<=", threshold=3.5),
        TisdaleItem(id="age_ge_68", type="boolean", points=2),
    ]
    bands = [TisdaleBand("low", 2, None), TisdaleBand("moderate", 4, None), TisdaleBand("high", None, 5)]
    return TisdaleScore("tisdale_2013", "doi", "VERIFIED", tuple(items), tuple(bands))


def _phi_crossing():
    """Phi crosses zero at k = 3.9: phi = (k - 3.9)."""

    def _eval(state: StateSpec) -> PhiEval:
        return PhiEval(phi=state.k_o_mM - 3.9, qnet=state.k_o_mM - 3.9 + 0.075, credibility="VERIFIED")

    return _eval


def test_insensitivity_interval_detected():
    score = _score()
    x0 = make_state(k_o_mM=5.0, m=1.0)
    sweep = {"variable": "k_o_mM", "from": 5.0, "to": 3.6, "n_points": 21}
    res = run_blindspot(_phi_crossing(), x0, sweep, score, {"age_ge_68": True}, margin_cfg(), qnet_ctrl=0.075)
    assert len(res.insensitivity_intervals) >= 1
    assert res.crossing_point is not None and abs(res.crossing_point - 3.9) < 0.2
    assert "insensitive to this" in res.verdict


def test_band_constant_while_phi_moves():
    score = _score()
    x0 = make_state(k_o_mM=5.0, m=1.0)
    sweep = {"variable": "k_o_mM", "from": 5.0, "to": 3.6, "n_points": 21}
    res = run_blindspot(_phi_crossing(), x0, sweep, score, {"age_ge_68": True}, margin_cfg(), qnet_ctrl=0.075)
    # score band should be constant (low) across the whole sweep because serum_k item
    # only triggers at <= 3.5 which is below the sweep floor 3.6
    assert len(set(res.score_band)) == 1
