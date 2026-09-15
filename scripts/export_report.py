#!/usr/bin/env python3
"""CLI report generation (§20.8). Requires model + VERIFIED data; fails safely otherwise."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import load_configs  # noqa: E402
from app.data.drug_registry import DrugRegistry  # noqa: E402
from app.services.errors import TorsadeTwinError  # noqa: E402


def main() -> int:
    cfg = load_configs(ROOT)
    try:
        DrugRegistry(ROOT / "data" / "drug_parameters.csv", ROOT / "data" / "drug_registry.yaml")
    except TorsadeTwinError as exc:
        print(f"REPORT BLOCKED: {exc.code}: {exc.message}")
        return 1
    print("Report export requires a computed result; run the API /report endpoint once the model is built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
