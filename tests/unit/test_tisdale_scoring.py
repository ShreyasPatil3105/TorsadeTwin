from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backend.app.data.scores import load_tisdale, score_tisdale
from backend.app.services.errors import TorsadeTwinError

TISDALE_VERIFIED = """
score_id: tisdale_2013
source_doi: "10.1161/CIRCOUTCOMES.113.000152"
verification_status: VERIFIED
items:
  - {id: age_ge_68, type: boolean, points: 2}
  - {id: female_sex, type: boolean, points: 1}
  - {id: loop_diuretic, type: boolean, points: 1}
  - {id: serum_k_le_3_5, type: threshold, variable: k_o_mM, operator: "<=", threshold: 3.5, points: 2}
  - {id: admission_qtc_ge_450, type: boolean, points: 2}
  - {id: acute_mi, type: boolean, points: 2}
  - {id: qt_prolonging_drugs_count, type: categorical, points_map: {one: 3, two_or_more: 6}}
  - {id: sepsis, type: boolean, points: 3}
  - {id: heart_failure, type: boolean, points: 2}
bands:
  - {label: low, max_inclusive: 6}
  - {label: moderate, max_inclusive: 10}
  - {label: high, min_inclusive: 11}
"""


def _load():
    d = Path(tempfile.mkdtemp())
    p = d / "tisdale.yaml"
    p.write_text(TISDALE_VERIFIED)
    return load_tisdale(p)


def test_placeholder_refused():
    d = Path(tempfile.mkdtemp())
    p = d / "tisdale.yaml"
    p.write_text(TISDALE_VERIFIED.replace("VERIFIED", "PLACEHOLDER"))
    with pytest.raises(TorsadeTwinError) as ei:
        load_tisdale(p)
    assert ei.value.code == "E_PROVENANCE_INCOMPLETE"


def test_item_points_and_bands():
    s = _load()
    assert s.band_for(5) == "low"
    assert s.band_for(8) == "moderate"
    assert s.band_for(12) == "high"


def test_unknown_items_give_interval():
    s = _load()
    # All other items known; only age_ge_68 (2) and female_sex (1) are UNKNOWN
    inputs = {"age_ge_68": "UNKNOWN", "female_sex": "UNKNOWN", "loop_diuretic": False,
              "admission_qtc_ge_450": False, "acute_mi": False, "sepsis": False,
              "heart_failure": False, "qt_prolonging_drugs_count": "one"}
    lo, hi = score_tisdale(s, inputs, k_o_mM=5.0)
    assert lo == 3  # qt_prolonging_drugs_count "one" = 3
    assert hi == 3 + 2 + 1  # + age_ge_68 (2) + female_sex (1)


def test_threshold_behaviour_at_3_5():
    s = _load()
    base = {"age_ge_68": False, "female_sex": False, "loop_diuretic": False,
            "admission_qtc_ge_450": False, "acute_mi": False, "sepsis": False,
            "heart_failure": False, "qt_prolonging_drugs_count": "one"}
    lo_35, hi_35 = score_tisdale(s, base, k_o_mM=3.5)
    lo_36, hi_36 = score_tisdale(s, base, k_o_mM=3.6)
    # threshold item (serum_k_le_3_5, 2 points) triggers only at <= 3.5
    assert lo_35 == lo_36 + 2
    assert hi_35 == hi_36 + 2
    assert lo_35 == hi_35  # all known -> point value


def test_full_known_inputs_point_value():
    s = _load()
    inputs = {"age_ge_68": True, "female_sex": True, "loop_diuretic": True, "admission_qtc_ge_450": True,
              "acute_mi": False, "sepsis": False, "heart_failure": True, "qt_prolonging_drugs_count": "two_or_more"}
    lo, hi = score_tisdale(s, inputs, k_o_mM=3.4)
    assert lo == hi  # no unknown -> point value
    assert lo == 2 + 1 + 1 + 2 + 2 + 6 + 2
