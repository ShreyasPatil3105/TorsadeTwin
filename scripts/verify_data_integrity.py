#!/usr/bin/env python3
"""Data integrity checks (§15.4): every parameter row has a DOI; no file listed in
data/FORBIDDEN_MANIFEST.txt exists; all verification_status values are legal.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"VERIFIED", "PLACEHOLDER", "REJECTED"}


def main() -> int:
    errors: list[str] = []
    csv_path = ROOT / "data" / "drug_parameters.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["ic50_nM"].strip() not in ("", "NA"):
                if not row["source_doi"].strip():
                    errors.append(f"{row['drug_id']}/{row['channel']}: missing DOI")
            status = row["verification_status"].strip()
            if status not in VALID_STATUSES:
                errors.append(f"{row['drug_id']}/{row['channel']}: bad status {status}")
    manifest = ROOT / "data" / "FORBIDDEN_MANIFEST.txt"
    if manifest.exists():
        for line in manifest.read_text("utf-8").splitlines():
            line = line.strip()
            if line and (ROOT / "data" / line).exists():
                errors.append(f"forbidden licensed file present: data/{line}")
    if errors:
        print("DATA INTEGRITY FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Data integrity OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
