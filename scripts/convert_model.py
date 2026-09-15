#!/usr/bin/env python3
"""CellML -> .mmt conversion + audits (§3.2).

Imports the vendored CellML via myokit.formats.cellml, writes models/ord_cipa_v1.mmt
(committed), dumps the state-variable list to models/STATE_VARIABLES.md, prints the
model's effective conductance constants for the scaling audit, and writes the Myokit
Python export used ONLY by V-9 (models/generated/ord_rhs.py).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        import myokit  # type: ignore
    except ImportError as exc:
        print("ERROR: myokit is not installed. Run `pip install -r backend/requirements.txt` (network once).")
        return 1
    cellml = ROOT / "models" / "vendor" / "ohara_rudy_cipa_v1_2017.cellml"
    if not cellml.exists():
        print("ERROR: vendored CellML missing. Run scripts/fetch_model.py first (network once).")
        return 1
    # The CellML importer lives in myokit.formats.cellml and is NOT auto-imported by
    # `import myokit`, so the submodule must be imported explicitly before use. If this
    # Myokit version ships without the CellML importer, fail safely with a clear
    # diagnostic — never invent a workaround or modify the downloaded model.
    try:
        import myokit.formats.cellml  # noqa: F401  (binds myokit.formats.cellml)
    except (ImportError, AttributeError) as exc:
        print(
            "ERROR: myokit.formats.cellml is unavailable in this Myokit version "
            f"({myokit.__version__}). The downloaded O'Hara-Rudy-CiPA CellML cannot be "
            "converted directly by this Myokit install. The model was not modified and no "
            "workaround was applied. Use a Myokit release that still ships the CellML "
            "importer, or an external CellML-to-MMt converter approved by the Chief Scientist."
        )
        return 1
    model = myokit.formats.cellml.load_model(str(cellml))
    out = ROOT / "models" / "ord_cipa_v1.mmt"
    myokit.save_model(model, str(out))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (ROOT / "models" / "CHECKSUMS.txt").write_text(f"{digest}  {out.name}\n")

    lines = ["# State variables of the vendored ORd-CiPA v1.0 model (ordered as in the .mmt)", ""]
    for var in model.states():
        lines.append(f"- {var}")
    (ROOT / "models" / "STATE_VARIABLES.md").write_text("\n".join(lines) + "\n")

    audit = ["# Scaling audit (Dutta 2017 optimised multipliers)", ""]
    for name in ["IKr.g", "IKs.g", "IK1.g", "ICaL.g", "INaL.g", "g_Kr", "g_Ks", "g_K1", "g_CaL", "g_NaL"]:
        if name in model:
            audit.append(f"{name} = {model.get(name).value()}")
    (ROOT / "models" / "SCALING_AUDIT.md").write_text("\n".join(audit) + "\n")
    print("Scaling audit written to models/SCALING_AUDIT.md")
    print("IMPORTANT: if the vendored CellML already embeds the Dutta 2017 factors, set")
    print("configs/model.yaml: apply_dutta_scaling: false. Double-scaling is a build-blocking bug.")

    (ROOT / "models" / "generated").mkdir(parents=True, exist_ok=True)
    try:
        py = myokit.formats.python.PythonModuleGenerator(model)
        (ROOT / "models" / "generated" / "ord_rhs.py").write_text(py.module())
        print("Python RHS export written to models/generated/ord_rhs.py (V-9 only)")
    except Exception as exc:
        print(f"WARNING: python export failed: {exc}")
    print(f"OK: {out} (sha256 {digest[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
