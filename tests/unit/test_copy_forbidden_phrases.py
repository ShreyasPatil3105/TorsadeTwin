from __future__ import annotations

from pathlib import Path

from backend.app.copy.disclaimers import DISCLAIMERS, FORBIDDEN_PHRASES

ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ["backend", "frontend/src", "docs", "README.md"]
# The definition file is the single source of the forbidden list itself; it must not be scanned.
EXCLUDE_FILES = {ROOT / "backend" / "app" / "copy" / "disclaimers.py"}


def _normalise(s: str) -> str:
    return " ".join(s.lower().split())


def test_forbidden_phrases_absent():
    # The approved disclaimer strings ("Not clinically validated" etc.) are required by §1.9
    # and are NOT forbidden claims; strip them from scanned text before matching.
    approved = [DISCLAIMERS[k] for k in DISCLAIMERS]
    hits = []
    for rel in SCAN_DIRS:
        p = ROOT / rel
        if p.is_file():
            files = [p]
        else:
            files = sorted(p.rglob("*"))
        for f in files:
            if f in EXCLUDE_FILES:
                continue
            if f.suffix in (".py", ".ts", ".tsx", ".md", ".json", ".yaml", ".yml", ".css", ".html"):
                text = f.read_text("utf-8", errors="ignore")
                for a in approved:
                    text = text.replace(a, "")
                norm = _normalise(text)
                for phrase in FORBIDDEN_PHRASES:
                    if _normalise(phrase) in norm:
                        hits.append((str(f), phrase))
    assert hits == [], f"Forbidden phrases found: {hits}"
