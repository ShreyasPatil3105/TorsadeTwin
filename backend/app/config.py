# Config loader: loads configs/*.yaml into frozen dataclasses; computes config_hash (§2.2, §18.3).
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .services.hashing import config_hash as compute_config_hash


@dataclass(frozen=True)
class Config:
    model: dict
    solver: dict
    protocol: dict
    domains: dict
    thresholds: dict
    margin: dict
    rescue: dict
    runtime: dict
    state_scales: dict
    config_hash: str


def load_configs(root: Path) -> Config:
    def _load(name: str) -> dict:
        p = root / "configs" / name
        if not p.exists():
            raise FileNotFoundError(f"Missing config: {p}")
        return yaml.safe_load(p.read_text("utf-8"))

    model = _load("model.yaml")
    solver = _load("solver.yaml")
    protocol = _load("protocol.yaml")
    domains = _load("domains.yaml")
    thresholds = _load("thresholds.yaml")
    margin = _load("margin.yaml")
    rescue = _load("rescue.yaml")
    runtime = _load("runtime.yaml")
    state_scales = _load("state_scales.yaml")

    # config_hash per §18.3 (drug parameter digest from registry)
    from backend.app.data.drug_registry import DrugRegistry

    _reg = DrugRegistry(
        root / "data" / "drug_parameters.csv",
        root / "data" / "drug_registry.yaml",
    )
    _digest = _reg.parameter_digest()

    cfg_hash = compute_config_hash(
        model_block=model,
        solver_block=solver,
        protocol_block=protocol,
        thresholds_block=thresholds,
        margin_block=margin,
        rescue_block=rescue,
        drug_parameter_digest=_digest,
    )
    return Config(model=model, solver=solver, protocol=protocol, domains=domains,
                  thresholds=thresholds, margin=margin, rescue=rescue, runtime=runtime,
                  state_scales=state_scales, config_hash=cfg_hash)
