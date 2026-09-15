from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

from backend.app.data.drug_registry import DrugRegistry
from backend.app.services.errors import TorsadeTwinError

HEADER = [
    "drug_id", "drug_name", "channel", "ic50_nM", "hill", "ic50_ci_low_nM", "ic50_ci_high_nM",
    "n_replicates", "assay", "temperature_C", "source_citation", "source_doi", "source_table",
    "units_check", "na_reason", "verification_status", "transcribed_by", "transcribed_on",
]


def _write(csv_rows: list[list], registry_yaml: str) -> tuple[Path, Path]:
    d = Path(tempfile.mkdtemp())
    csv_path = d / "drug_parameters.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HEADER)
        for r in csv_rows:
            w.writerow(r)
    yaml_path = d / "drug_registry.yaml"
    yaml_path.write_text(registry_yaml)
    return csv_path, yaml_path


REG = """
drugs:
  - drug_id: dofetilide
    drug_name: Dofetilide
    cmax_free_nM: 2.0
    cmax_source_doi: "10.1002/cpt.1184"
    max_validated_multiple: 25
    discontinuable: false
    dose_steps: [1.0, 0.75, 0.5, 0.25]
    cipa_training_risk_label: high
    qt_risk_class_manual: null
    notes: ""
"""


def _verified_row(drug="dofetilide", channel="IKr", ic50="100.0", hill="1.0"):
    return [drug, "Dofetilide", channel, ic50, hill, "", "", "3", "manual patch clamp", "37",
            "Crumb 2016", "10.1016/j.vascn.2016.03.009", "Table 2", "IC50_nM|hill_dimensionless",
            "", "VERIFIED", "alice", "2026-09-01"]


def test_verified_registry_loads():
    csv_path, yaml_path = _write([_verified_row()], REG)
    reg = DrugRegistry(csv_path, yaml_path)
    assert reg.has("dofetilide")
    rec = reg.get("dofetilide")
    assert rec.cmax_free_nM == 2.0
    assert rec.block_for("IKr").ic50_nM == 100.0


def test_placeholder_row_refused():
    row = _verified_row()
    row[3] = "PLACEHOLDER"
    row[4] = "PLACEHOLDER"
    row[15] = "PLACEHOLDER"
    csv_path, yaml_path = _write([row], REG)
    with pytest.raises(TorsadeTwinError) as ei:
        DrugRegistry(csv_path, yaml_path)
    assert ei.value.code == "E_PROVENANCE_INCOMPLETE"


def test_missing_doi_refused():
    row = _verified_row()
    row[11] = ""
    csv_path, yaml_path = _write([row], REG)
    with pytest.raises(TorsadeTwinError) as ei:
        DrugRegistry(csv_path, yaml_path)
    assert ei.value.code == "E_PROVENANCE_INCOMPLETE"


def test_na_row_with_reason_ok():
    row = _verified_row(channel="IKs")
    row[3] = "NA"
    row[4] = ""
    row[14] = "no data in source"
    csv_path, yaml_path = _write([row], REG)
    reg = DrugRegistry(csv_path, yaml_path)
    assert reg.get("dofetilide").partial_panel == ["IKs"]


def test_unknown_drug():
    csv_path, yaml_path = _write([_verified_row()], REG)
    reg = DrugRegistry(csv_path, yaml_path)
    with pytest.raises(TorsadeTwinError) as ei:
        reg.get("nope")
    assert ei.value.code == "E_UNKNOWN_DRUG"
