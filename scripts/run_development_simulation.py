#!/usr/bin/env python3
"""Run the requested short real-model development case."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import load_configs
from backend.app.ep.model_loader import ModelLoader
from backend.app.ep.simulate import EpEngine
from backend.app.schemas.common import StateSpec


def main() -> None:
    cfg = load_configs(ROOT)
    model_path = ROOT / cfg.model["artefact"]
    info = ModelLoader(cfg.model, ROOT / "models" / "CHECKSUMS.txt", model_path).load()
    engine = EpEngine(
        info,
        cfg.solver["profiles"]["standard"],
        cfg.protocol,
        cfg.state_scales,
    )
    state = StateSpec(drugs=[], k_o_mM=5.4, cl_ms=2000)
    unblocked = {channel: 1.0 for channel in ("IKr", "ICaL", "INaL", "IKs", "IK1", "Ito")}
    result = engine.simulate(state, unblocked, return_trace=False)
    payload = asdict(result)
    payload.pop("state_vector", None)
    payload.pop("trace_t_ms", None)
    payload.pop("trace_v_mV", None)
    payload.pop("trace_i_net_A_per_F", None)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
