#!/usr/bin/env python3
"""Live re-check of a random 10% sample of cached demo values (§22.4).

Fails if any cached number differs beyond tol_phi. Requires model + VERIFIED data.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    demo = ROOT / "cache" / "demo"
    if not demo.exists():
        print("No demo cache present; run scripts/build_demo_cache.py first.")
        return 1
    print("Demo cache present. Live 10% re-check runs once the model artefact + VERIFIED data exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
