# L2 — Drug parameter layer (§5.2, §5.3, §2.2 L2).
# Loads drug_parameters.csv + drug_registry.yaml; refuses to serve any row lacking
# source_doi or with verification_status != VERIFIED. Never invents pharmacology values.
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ..services.errors import TorsadeTwinError

VALID_STATUSES = {"VERIFIED", "PLACEHOLDER", "REJECTED"}
VALID_CHANNELS = {"IKr", "ICaL", "INa_peak", "INaL", "IKs", "Ito", "IK1"}
VALID_UNITS = {"IC50_nM|hill_dimensionless"}

CSV_COLUMNS = [
    "drug_id", "drug_name", "channel", "ic50_nM", "hill", "ic50_ci_low_nM", "ic50_ci_high_nM",
    "n_replicates", "assay", "temperature_C", "source_citation", "source_doi", "source_table",
    "units_check", "na_reason", "verification_status", "transcribed_by", "transcribed_on",
]


@dataclass(frozen=True)
class ChannelBlock:
    channel: str
    ic50_nM: float | None
    hill: float | None
    ic50_ci_low_nM: float | None = None
    ic50_ci_high_nM: float | None = None
    n_replicates: int | None = None
    assay: str = ""
    temperature_C: float | None = None
    source_citation: str = ""
    source_doi: str = ""
    source_table: str = ""
    na_reason: str = ""
    verification_status: str = "PLACEHOLDER"
    transcribed_by: str = ""
    transcribed_on: str = ""

    @property
    def is_na(self) -> bool:
        return self.ic50_nM is None

    @property
    def runtime_excluded(self) -> bool:
        """True when this row must not enter runtime pharmacology."""
        return self.ic50_nM is None or self.verification_status != "VERIFIED"


@dataclass(frozen=True)
class DrugRecord:
    drug_id: str
    drug_name: str
    cmax_free_nM: float
    cmax_source_doi: str
    max_validated_multiple: float
    discontinuable: bool
    dose_steps: tuple[float, ...]
    cipa_training_risk_label: str
    qt_risk_class_manual: str | None
    notes: str
    channels: tuple[ChannelBlock, ...] = field(default_factory=tuple)

    @property
    def partial_panel(self) -> list[str]:
        return [c.channel for c in self.channels if c.runtime_excluded]

    def block_for(self, channel: str) -> ChannelBlock | None:
        for c in self.channels:
            if c.channel == channel:
                return c
        return None


def _parse_float_or_none(raw: str) -> float | None:
    raw = raw.strip()
    if raw == "" or raw.upper() in ("NA", "PLACEHOLDER"):
        return None
    return float(raw)


def _parse_na_reason(raw: str) -> str:
    return raw.strip()


class DrugRegistry:
    """Immutable registry built once at startup; provenance gate enforced at load."""

    def __init__(self, csv_path: Path, yaml_path: Path):
        self._records: dict[str, DrugRecord] = {}
        self._load(csv_path, yaml_path)
        self._freeze()

    def _load(self, csv_path: Path, yaml_path: Path) -> None:
        if not csv_path.exists() or not yaml_path.exists():
            raise TorsadeTwinError(
                "E_PROVENANCE_INCOMPLETE",
                "Drug data files missing.",
                detail=f"Expected {csv_path} and {yaml_path}.",
                remediation="Restore data/drug_parameters.csv and data/drug_registry.yaml.",
                http_status=503,
            )
        meta = yaml.safe_load(yaml_path.read_text("utf-8"))
        meta_by_id: dict[str, dict] = {m["drug_id"]: m for m in meta.get("drugs", meta if isinstance(meta, list) else [])}

        rows: dict[str, list[ChannelBlock]] = {}
        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or [c.strip() for c in reader.fieldnames] != CSV_COLUMNS:
                raise TorsadeTwinError(
                    "E_UNITS", "Drug CSV schema mismatch.",
                    detail=f"Expected columns {CSV_COLUMNS}.", http_status=503,
                )
            for row in reader:
                drug_id = row["drug_id"].strip()
                channel = row["channel"].strip()
                if channel not in VALID_CHANNELS:
                    raise TorsadeTwinError("E_UNITS", f"Unknown channel {channel} in drug CSV.", http_status=503)
                units = row["units_check"].strip()
                if units != "IC50_nM|hill_dimensionless":
                    raise TorsadeTwinError("E_UNITS", f"Bad units_check for {drug_id}/{channel}: {units}.", http_status=503)
                status = row["verification_status"].strip()
                if status not in VALID_STATUSES:
                    raise TorsadeTwinError("E_UNITS", f"Bad verification_status {status} for {drug_id}/{channel}.", http_status=503)
                ic50 = _parse_float_or_none(row["ic50_nM"])
                hill = _parse_float_or_none(row["hill"])
                na_reason = _parse_na_reason(row.get("na_reason", ""))
                if ic50 is None and hill is not None:
                    raise TorsadeTwinError("E_UNITS", f"NA row {drug_id}/{channel} must not carry hill.", http_status=503)
                doi = row["source_doi"].strip()
                if ic50 is not None:
                    if ic50 <= 0:
                        raise TorsadeTwinError("E_UNITS", f"Non-positive IC50 for {drug_id}/{channel}.", http_status=503)
                    if hill is not None and status != "REJECTED" and not (0.5 <= hill <= 3.0):
                        raise TorsadeTwinError("E_UNITS", f"Hill out of [0.5,3.0] for {drug_id}/{channel}.", http_status=503)
                    if not doi:
                        raise TorsadeTwinError("E_PROVENANCE_INCOMPLETE", f"Missing DOI for {drug_id}/{channel}.", http_status=503)
                rows.setdefault(drug_id, []).append(
                    ChannelBlock(
                        channel=channel,
                        ic50_nM=ic50,
                        hill=hill,
                        ic50_ci_low_nM=_parse_float_or_none(row.get("ic50_ci_low_nM", "")),
                        ic50_ci_high_nM=_parse_float_or_none(row.get("ic50_ci_high_nM", "")),
                        n_replicates=_parse_int_or_none(row.get("n_replicates", "")),
                        assay=row.get("assay", "").strip(),
                        temperature_C=_parse_float_or_none(row.get("temperature_C", "")),
                        source_citation=row.get("source_citation", "").strip(),
                        source_doi=doi,
                        source_table=row.get("source_table", "").strip(),
                        na_reason=na_reason,
                        verification_status=status,
                        transcribed_by=row.get("transcribed_by", "").strip(),
                        transcribed_on=row.get("transcribed_on", "").strip(),
                    )
                )
        for drug_id, m in meta_by_id.items():
            if drug_id not in rows:
                raise TorsadeTwinError("E_PROVENANCE_INCOMPLETE", f"Registry entry {drug_id} has no CSV rows.", http_status=503)
            cmax_raw = m["cmax_free_nM"]
            if isinstance(cmax_raw, str) and cmax_raw.strip().upper() in ("PLACEHOLDER", "NA", "<TRANSCRIBE>"):
                raise TorsadeTwinError(
                    "E_PROVENANCE_INCOMPLETE",
                    f"Registry entry {drug_id} has a PLACEHOLDER cmax_free_nM; a human must transcribe it "
                    "from Li et al. 2019 (doi:10.1002/cpt.1184) and mark it VERIFIED.",
                    detail="cmax_free_nM must be a numeric free C_max value with cmax_basis: free.",
                    remediation="Transcribe from the cited source table (see validation/transcription_log.md).",
                    http_status=503,
                )
            self._records[drug_id] = DrugRecord(
                drug_id=drug_id,
                drug_name=m["drug_name"],
                cmax_free_nM=float(cmax_raw),
                cmax_source_doi=m.get("cmax_source_doi", ""),
                max_validated_multiple=float(m.get("max_validated_multiple", 25)),
                discontinuable=bool(m.get("discontinuable", False)),
                dose_steps=tuple(float(x) for x in m.get("dose_steps", [1.0, 0.75, 0.5, 0.25])),
                cipa_training_risk_label=str(m.get("cipa_training_risk_label", "")),
                qt_risk_class_manual=m.get("qt_risk_class_manual"),
                notes=str(m.get("notes", "")),
                channels=tuple(rows[drug_id]),
            )

    def _freeze(self) -> None:
        for rec in self._records.values():
            for c in rec.channels:
                if c.verification_status not in ("VERIFIED", "REJECTED"):
                    raise TorsadeTwinError(
                        "E_PROVENANCE_INCOMPLETE",
                        f"Drug parameter for {rec.drug_id}/{c.channel} is {c.verification_status}; "
                        "refusing to serve until a human transcribes and verifies it.",
                        detail="Rows must be marked VERIFIED with source_doi, transcribed_by and a reviewer, or REJECTED if source data is out of runtime schema.",
                        remediation="Transcribe from the cited source table and mark VERIFIED (see validation/transcription_log.md), or mark REJECTED if source data is out of the [0.5,3.0] hill range.",
                        http_status=503,
                    )

    def get(self, drug_id: str) -> DrugRecord:
        if drug_id not in self._records:
            raise TorsadeTwinError("E_UNKNOWN_DRUG", f"Unknown drug id: {drug_id}.", detail="Not in drug_registry.yaml.")
        return self._records[drug_id]

    def has(self, drug_id: str) -> bool:
        return drug_id in self._records

    def all(self) -> list[DrugRecord]:
        return [self._records[k] for k in sorted(self._records)]

    def parameter_digest(self) -> str:
        """Stable digest of the parameter table for config_hash (§18.3)."""
        import hashlib

        lines = []
        for rec in self.all():
            for c in rec.channels:
                lines.append(f"{rec.drug_id}|{c.channel}|{c.ic50_nM}|{c.hill}|{c.source_doi}|{c.verification_status}")
        return hashlib.sha256("\n".join(sorted(lines)).encode("utf-8")).hexdigest()


def _parse_int_or_none(raw: str) -> int | None:
    raw = raw.strip()
    if raw == "":
        return None
    return int(float(raw))
