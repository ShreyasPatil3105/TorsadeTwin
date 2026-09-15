from __future__ import annotations

import pytest

from backend.app.schemas.common import StateSpec
from backend.app.services.errors import TorsadeTwinError


def test_domains_defaults():
    s = StateSpec()
    assert s.k_o_mM == 5.4
    assert s.cl_ms == 2000
    assert s.solver_profile.value == "standard"


def test_domains_range_rejects():
    for k in [2.4, 7.1]:
        with pytest.raises(Exception):
            StateSpec.model_validate({"k_o_mM": k})
    for cl in [499, 2001]:
        with pytest.raises(Exception):
            StateSpec.model_validate({"cl_ms": cl})


def test_exposure_tag_out_of_calibrated_range():
    # > max_validated_multiple (25) is rejected at schema level (domain); the tag applies
    # when the value is inside the model domain but above the calibrated band.
    from backend.app.engines.verification import apply_downgrade_tags

    assert apply_downgrade_tags("VERIFIED", ["OUT_OF_CALIBRATED_RANGE"]) == "UNVERIFIED"
    assert apply_downgrade_tags("VERIFIED", ["OUT_OF_PHYSIOLOGICAL_RANGE"]) == "UNVERIFIED"
    assert apply_downgrade_tags("VERIFIED", ["COMBO_RULE_SENSITIVE"]) == "UNVERIFIED"
    assert apply_downgrade_tags("VERIFIED", ["partial_panel"]) == "UNVERIFIED"
    assert apply_downgrade_tags("VERIFIED", ["ARTEFACT_SUSPECTED"]) == "UNVERIFIED"
    assert apply_downgrade_tags("VERIFIED", ["BUDGET_EXCEEDED"]) == "UNVERIFIED"
    assert apply_downgrade_tags("VERIFIED", []) == "VERIFIED"
