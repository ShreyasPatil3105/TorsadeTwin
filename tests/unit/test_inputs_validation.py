from __future__ import annotations

import pytest

from backend.app.schemas.common import DrugExposure, StateSpec
from backend.app.services.errors import TorsadeTwinError


def _valid() -> dict:
    return {"drugs": [{"drug_id": "dofetilide", "exposure_multiplier": 1.0}], "k_o_mM": 4.0, "cl_ms": 2000}


def test_valid_state():
    s = StateSpec.model_validate(_valid())
    assert s.k_o_mM == 4.0
    assert s.cl_ms == 2000
    assert s.cell_type.value == "endo"


def test_unknown_drug_is_schema_agnostic():
    # drug existence is checked by the registry, not the schema; unknown ids pass schema
    s = StateSpec.model_validate({"drugs": [{"drug_id": "nope", "exposure_multiplier": 1.0}], "k_o_mM": 4.0})
    assert s.drugs[0].drug_id == "nope"


def test_reject_k_out_of_domain():
    with pytest.raises(Exception):
        StateSpec.model_validate({"k_o_mM": 8.0})
    with pytest.raises(Exception):
        StateSpec.model_validate({"k_o_mM": 1.0})


def test_reject_exposure_out_of_domain():
    with pytest.raises(Exception):
        StateSpec.model_validate({"drugs": [{"drug_id": "d", "exposure_multiplier": 26.0}]})
    with pytest.raises(Exception):
        StateSpec.model_validate({"drugs": [{"drug_id": "d", "exposure_multiplier": -1.0}]})


def test_reject_cl_out_of_domain():
    with pytest.raises(Exception):
        StateSpec.model_validate({"cl_ms": 499})
    with pytest.raises(Exception):
        StateSpec.model_validate({"cl_ms": 2001})


def test_reject_duplicate_drugs():
    with pytest.raises(Exception):
        StateSpec.model_validate({"drugs": [{"drug_id": "d", "exposure_multiplier": 1.0},
                                            {"drug_id": "d", "exposure_multiplier": 2.0}]})


def test_reject_more_than_4_drugs():
    drugs = [{"drug_id": f"d{i}", "exposure_multiplier": 1.0} for i in range(5)]
    with pytest.raises(Exception):
        StateSpec.model_validate({"drugs": drugs})


def test_canonical_hash_stable_under_key_reordering():
    from backend.app.services.hashing import input_hash

    a = StateSpec.model_validate(_valid())
    b = StateSpec.model_validate({"cl_ms": 2000, "k_o_mM": 4.0, "drugs": [{"exposure_multiplier": 1.0, "drug_id": "dofetilide"}]})
    assert input_hash(a.to_canonical()) == input_hash(b.to_canonical())


def test_canonical_hash_float_formatting():
    from backend.app.services.hashing import canonical_json

    assert canonical_json({"x": 0.1}) == canonical_json({"x": 0.10000000000000001})
