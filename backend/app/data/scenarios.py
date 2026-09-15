# Scenario loader (§22.1, §2.2 L1). All scenarios are synthetic, declared, non-identifiable.
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..services.errors import TorsadeTwinError


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    synthetic: bool
    title: str
    state: dict
    score_inputs: dict
    notes: str = ""


def load_scenarios(dir_path: Path) -> dict[str, Scenario]:
    out: dict[str, Scenario] = {}
    for p in sorted(dir_path.glob("*.yaml")):
        data = yaml.safe_load(p.read_text("utf-8"))
        if not data.get("synthetic", False):
            raise TorsadeTwinError(
                "E_SCHEMA",
                f"Scenario {data.get('scenario_id')} must declare synthetic: true (D5).",
            )
        out[data["scenario_id"]] = Scenario(
            scenario_id=data["scenario_id"],
            synthetic=bool(data["synthetic"]),
            title=data.get("title", ""),
            state=data["state"],
            score_inputs=data.get("score_inputs", {}),
            notes=data.get("notes", ""),
        )
    return out
