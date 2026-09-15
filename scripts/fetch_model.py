#!/usr/bin/env python3
"""ONE-TIME network step: download the CellML artefact (§3.2).

Downloads ohara_rudy_cipa_v1_2017.cellml to models/vendor/, records SHA-256 in
models/vendor/CHECKSUMS.txt and source URL + retrieval date in models/vendor/PROVENANCE.yaml.
After this step the system never needs the network (A6).
"""
from __future__ import annotations

import datetime
import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://models.cellml.org/e/5a0/raw"
DEST = ROOT / "models" / "vendor" / "ohara_rudy_cipa_v1_2017.cellml"


def main() -> int:
    print(f"Fetching {URL} ...")
    try:
        with urllib.request.urlopen(URL, timeout=120) as resp:
            data = resp.read()
    except Exception as exc:
        print(f"ERROR: download failed (network required once): {exc}")
        return 1
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (ROOT / "models" / "vendor" / "CHECKSUMS.txt").write_text(f"{digest}  {DEST.name}\n")
    provenance = (
        "source_url: https://models.cellml.org/e/5a0\n"
        f"retrieved_on: {datetime.date.today().isoformat()}\n"
        f"sha256: {digest}\n"
        "licence: record licence text as published by Physiome Model Repository\n"
    )
    (ROOT / "models" / "vendor" / "PROVENANCE.yaml").write_text(provenance)
    print(f"OK: {DEST} ({len(data)} bytes, sha256 {digest[:16]}...)")
    print("Next: scripts/convert_model.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
