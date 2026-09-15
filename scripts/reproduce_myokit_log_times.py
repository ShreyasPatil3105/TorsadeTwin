#!/usr/bin/env python3
"""Reproduce and verify consecutive explicit-log behavior with real Myokit."""
from __future__ import annotations

from pathlib import Path

import myokit
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "ord_cipa_v1.mmt"
LABELS = [
    "membrane.v",
    "IKr.IKr",
    "ICaL.ICaL",
    "INaL.INaL",
    "IKs.IKs",
    "IK1.IK1",
    "Ito.Ito",
]


def main() -> None:
    cl = 2000.0
    dt = 0.1
    relative = np.arange(int(round(cl / dt)), dtype=float) * dt

    broken = myokit.Simulation(myokit.load_model(MODEL))
    first = broken.run(cl, log_times=relative, log=LABELS)
    second = broken.run(cl, log_times=relative, log=LABELS)
    broken_counts = (len(first["membrane.v"]), len(second["membrane.v"]))

    fixed = myokit.Simulation(myokit.load_model(MODEL))
    start = fixed.time()
    first_fixed = fixed.run(cl, log_times=start + relative, log=LABELS)
    start = fixed.time()
    second_fixed = fixed.run(cl, log_times=start + relative, log=LABELS)
    fixed_counts = (len(first_fixed["membrane.v"]), len(second_fixed["membrane.v"]))

    precheck = myokit.Simulation(myokit.load_model(MODEL))
    precheck.pre(123.4)

    print(f"Myokit {myokit.__version__}")
    print(f"broken consecutive counts: {broken_counts}")
    print(f"shifted consecutive counts: {fixed_counts}")
    print(f"time after pre(123.4): {precheck.time()}")

    assert broken_counts == (20000, 0)
    assert fixed_counts == (20000, 20000)
    assert precheck.time() == 0.0


if __name__ == "__main__":
    main()
