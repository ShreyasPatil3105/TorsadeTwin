# Tisdale score loader + scorer (§13.2).
# Items/points must be transcribed by a human from Tisdale 2013 (doi:10.1161/CIRCOUTCOMES.113.000152);
# the loader refuses PLACEHOLDER rows. Missing scenario inputs are scored UNKNOWN -> interval.
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ..services.errors import TorsadeTwinError

VALID_STATUSES = {"VERIFIED", "PLACEHOLDER", "REJECTED"}


@dataclass(frozen=True)
class TisdaleItem:
    id: str
    type: str  # boolean | threshold | categorical
    points: int | dict | None
    variable: str | None = None
    operator: str | None = None
    threshold: float | None = None
    points_map: dict | None = None


@dataclass(frozen=True)
class TisdaleBand:
    label: str
    max_inclusive: int | None
    min_inclusive: int | None


@dataclass(frozen=True)
class TisdaleScore:
    score_id: str
    source_doi: str
    verification_status: str
    items: tuple[TisdaleItem, ...]
    bands: tuple[TisdaleBand, ...]

    def band_for(self, score: int) -> str | None:
        for b in self.bands:
            if b.max_inclusive is not None and score <= b.max_inclusive:
                return b.label
            if b.min_inclusive is not None and score >= b.min_inclusive:
                return b.label
        return None


def load_tisdale(path: Path) -> TisdaleScore:
    if not path.exists():
        raise TorsadeTwinError("E_PROVENANCE_INCOMPLETE", "Tisdale score file missing.", http_status=503)
    data = yaml.safe_load(path.read_text("utf-8"))
    status = data.get("verification_status", "PLACEHOLDER")
    if status not in VALID_STATUSES:
        raise TorsadeTwinError("E_UNITS", f"Bad tisdale verification_status: {status}.", http_status=503)
    if status != "VERIFIED":
        raise TorsadeTwinError(
            "E_PROVENANCE_INCOMPLETE",
            f"Tisdale score {data.get('score_id')} is {status}; a human must transcribe items/points "
            "from the cited paper and mark VERIFIED.",
            http_status=503,
        )
    items = []
    for it in data.get("items", []):
        items.append(
            TisdaleItem(
                id=it["id"],
                type=it["type"],
                points=it.get("points"),
                variable=it.get("variable"),
                operator=it.get("operator"),
                threshold=it.get("threshold"),
                points_map=it.get("points_map"),
            )
        )
    bands = [TisdaleBand(b["label"], b.get("max_inclusive"), b.get("min_inclusive")) for b in data.get("bands", [])]
    return TisdaleScore(
        score_id=data["score_id"],
        source_doi=data["source_doi"],
        verification_status=status,
        items=tuple(items),
        bands=tuple(bands),
    )


def score_tisdale(score: TisdaleScore, inputs: dict, k_o_mM: float | None) -> tuple[int, int]:
    """Return (score_min, score_max) over UNKNOWN items. Never a fake point value."""
    lo = 0
    hi = 0
    for it in score.items:
        if it.type == "boolean":
            val = inputs.get(it.id, "UNKNOWN")
            if val == "UNKNOWN":
                lo += 0
                hi += it.points if isinstance(it.points, int) else 0
            elif val:
                lo += it.points if isinstance(it.points, int) else 0
                hi += it.points if isinstance(it.points, int) else 0
        elif it.type == "threshold":
            # The ONLY item coupled to a modelled variable: serum_K := k_o_mM proxy (ASSUMPTION_SERUM_KO_PROXY_v1)
            if k_o_mM is None:
                lo += 0
                hi += it.points if isinstance(it.points, int) else 0
            else:
                hit = False
                if it.operator == "<=" and k_o_mM <= it.threshold:
                    hit = True
                elif it.operator == ">=" and k_o_mM >= it.threshold:
                    hit = True
                if hit:
                    lo += it.points if isinstance(it.points, int) else 0
                    hi += it.points if isinstance(it.points, int) else 0
        elif it.type == "categorical":
            val = inputs.get(it.id, "UNKNOWN")
            pm = it.points_map or {}
            if val == "UNKNOWN":
                lo += 0
                hi += max((v for v in pm.values() if isinstance(v, int)), default=0)
            else:
                pts = pm.get(val, 0)
                lo += pts if isinstance(pts, int) else 0
                hi += pts if isinstance(pts, int) else 0
    return lo, hi
