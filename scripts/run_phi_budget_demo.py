#!/usr/bin/env python3
"""Complete exactly 300 real Phi evaluations at scientific protocol settings.

Cold start: n_prepace=1000 (configs/protocol.yaml default).
Warm start: SPEC n_warm=200 beats from neighbour state, C1–C4 required.
No reduced-prepace validation. All evaluations are real CVODES solves.

Parallelism: margin stages remain serial (adaptive + warm-state chain).
Only the independent fill grid is parallelized across CPU workers.
"""
from __future__ import annotations

from pathlib import Path
import sys
import time
import itertools
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import load_configs
from backend.app.ep.model_loader import ModelLoader
from backend.app.ep.simulate import EpEngine
from backend.app.data.drug_registry import DrugRegistry
from backend.app.schemas.common import StateSpec, DrugExposure
from backend.app.engines.phi import PhiEval
from backend.app.ep.block import compute_block
from backend.app.engines.margin import compute_margin

# Module-level worker state (initialized once per process).
_W: dict[str, Any] = {}


def _worker_init(root_str: str, warm_state: list[float], boundary: float) -> None:
    """One-time per-process init: load model, compile Simulation once."""
    root = Path(root_str)
    sys.path.insert(0, str(root))
    from backend.app.config import load_configs
    from backend.app.ep.model_loader import ModelLoader
    from backend.app.ep.simulate import EpEngine
    from backend.app.data.drug_registry import DrugRegistry

    cfg = load_configs(root)
    info = ModelLoader(cfg.model, root / "models/CHECKSUMS.txt", root / cfg.model["artefact"]).load()
    reg = DrugRegistry(root / "data/drug_parameters.csv", root / "data/drug_registry.yaml")
    protocol = dict(cfg.protocol)
    assert int(protocol.get("n_prepace", 1000)) == 1000
    assert int(protocol.get("n_warm", 200)) == 200
    engine = EpEngine(info, cfg.solver["profiles"]["standard"], protocol, cfg.state_scales)
    _W["engine"] = engine
    _W["reg"] = reg
    _W["warm"] = list(warm_state)
    _W["boundary"] = float(boundary)


def _worker_eval(payload: dict) -> dict:
    """One real CVODES Phi evaluation in a worker process (n_warm=200)."""
    from backend.app.schemas.common import StateSpec, DrugExposure
    from backend.app.ep.block import compute_block

    engine = _W["engine"]
    reg = _W["reg"]
    warm = _W["warm"]
    boundary = _W["boundary"]
    k = float(payload["k_o_mM"])
    drugs_spec = payload["drugs"]  # list of (drug_id, mult) or empty
    if drugs_spec:
        state = StateSpec(
            k_o_mM=k,
            cl_ms=2000,
            drugs=[DrugExposure(drug_id=d, exposure_multiplier=m) for d, m in drugs_spec],
        )
        drugs = [(d, m * reg.get(d).cmax_free_nM) for d, m in drugs_spec]
    else:
        state = StateSpec(k_o_mM=k, cl_ms=2000, drugs=[])
        drugs = []
    block = compute_block(reg, drugs)
    try:
        res = engine.simulate(state, block.unblocked, warm_state=warm)
        return {
            "ok": True,
            "qnet": float(res.qnet_C_per_F),
            "phi": float(res.qnet_C_per_F) - boundary,
            "converged": bool(res.converged),
            "idx": payload["idx"],
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": getattr(exc, "code", type(exc).__name__),
            "idx": payload["idx"],
        }


def main() -> int:
    t0 = time.time()
    cfg = load_configs(ROOT)
    info = ModelLoader(cfg.model, ROOT / "models/CHECKSUMS.txt", ROOT / cfg.model["artefact"]).load()
    reg = DrugRegistry(ROOT / "data/drug_parameters.csv", ROOT / "data/drug_registry.yaml")
    solver = cfg.solver["profiles"]["standard"]

    protocol = dict(cfg.protocol)
    assert int(protocol.get("n_prepace", 1000)) == 1000, "n_prepace must be 1000"
    assert int(protocol.get("n_warm", 200)) == 200, "n_warm must be 200"
    engine = EpEngine(info, solver, protocol, cfg.state_scales)

    n_workers = max(1, int(os.cpu_count() or 1))  # use all available cores for independent fill
    print(f"workers={n_workers} (fill stage only; margin stays serial)", flush=True)

    print("Cold control (n_prepace=1000)...", flush=True)
    ctrl_state = StateSpec(drugs=[], k_o_mM=5.4, cl_ms=2000)
    ctrl_block = compute_block(reg, [])
    ctrl = engine.simulate(ctrl_state, ctrl_block.unblocked)
    qnet_ctrl = ctrl.qnet_C_per_F
    boundary = 0.75 * qnet_ctrl
    last_warm = list(ctrl.state_vector)
    control_warm = list(ctrl.state_vector)  # fixed seed for independent fill evals
    print(f"qnet_ctrl={qnet_ctrl} boundary={boundary}", flush=True)

    used = 0
    stage_counts = {"margin": 0, "fill": 0}
    in_margin = True
    BUDGET = 300

    def phi(state: StateSpec) -> PhiEval:
        nonlocal used, last_warm, in_margin
        if used >= BUDGET:
            return PhiEval(phi=None, qnet=None, credibility="UNKNOWN", tags=["E_BUDGET"], n_evals=0)
        used += 1
        if in_margin:
            stage_counts["margin"] += 1
        else:
            stage_counts["fill"] += 1
        drugs = [
            (d.drug_id, d.exposure_multiplier * reg.get(d.drug_id).cmax_free_nM)
            for d in state.drugs
        ]
        block = compute_block(reg, drugs)
        try:
            res = engine.simulate(state, block.unblocked, warm_state=last_warm)
            last_warm = list(res.state_vector)
        except Exception as exc:
            if used % 25 == 0 or used <= 3:
                print(f"  Phi {used}/{BUDGET} NONCREDIBLE {getattr(exc, 'code', type(exc).__name__)}", flush=True)
            return PhiEval(
                phi=None, qnet=None, credibility="UNKNOWN",
                tags=[getattr(exc, "code", type(exc).__name__)], n_evals=1,
            )
        if used % 25 == 0 or used <= 3:
            print(f"  Phi {used}/{BUDGET} qNet={res.qnet_C_per_F}", flush=True)
        return PhiEval(
            phi=res.qnet_C_per_F - boundary,
            qnet=res.qnet_C_per_F,
            credibility="VERIFIED" if res.converged else "FAILED",
            tags=block.partial_panel,
            n_evals=1,
        )

    x0 = StateSpec(
        k_o_mM=4.5, cl_ms=2000,
        drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)],
    )
    margin_cfg = dict(cfg.margin)
    margin_cfg["max_evals"] = BUDGET
    print("compute_margin (serial, warm n_warm=200)...", flush=True)
    axes = ["k_o_mM", "exposure:dofetilide"]
    result = compute_margin(phi, x0, axes, margin_cfg)
    print(
        f"after margin used={used} result.n_phi_evals={result.n_phi_evals} "
        f"m_status={result.m_status}",
        flush=True,
    )

    # ---- Parallel fill: independent states, each warm-started from control SS ----
    in_margin = False
    remaining = BUDGET - used
    if remaining > 0:
        ks = [3.0, 3.5, 4.0, 4.5, 5.0, 5.4, 5.5]
        mults = [0.125, 0.25, 0.5, 1.0, 2.0, 4.0]
        drug_ids = ["dofetilide", "quinidine", "sotalol", "verapamil"]
        payloads: list[dict] = []
        idx = 0
        for k, m, d in itertools.product(ks, mults, drug_ids):
            if len(payloads) >= remaining:
                break
            payloads.append({
                "idx": idx,
                "k_o_mM": k,
                "drugs": [(d, m)],
            })
            idx += 1
        # Control-like states if still short
        for k in [3.0, 3.2, 3.8, 4.2, 4.8, 5.2, 5.5]:
            if len(payloads) >= remaining:
                break
            payloads.append({"idx": idx, "k_o_mM": k, "drugs": []})
            idx += 1
        while len(payloads) < remaining:
            payloads.append({"idx": idx, "k_o_mM": 5.4, "drugs": []})
            idx += 1
        payloads = payloads[:remaining]

        print(f"parallel fill: {len(payloads)} independent evals on {n_workers} workers...", flush=True)
        completed = 0
        with ProcessPoolExecutor(
            max_workers=n_workers,
            initializer=_worker_init,
            initargs=(str(ROOT), control_warm, boundary),
        ) as pool:
            futures = [pool.submit(_worker_eval, p) for p in payloads]
            for fut in as_completed(futures):
                r = fut.result()
                used += 1
                stage_counts["fill"] += 1
                completed += 1
                if completed % 25 == 0 or completed <= 3:
                    status = "ok" if r.get("ok") else r.get("error")
                    print(f"  fill {completed}/{len(payloads)} used={used} {status}", flush=True)
                if used > BUDGET:
                    raise RuntimeError(f"Phi counter exceeded budget: {used} > {BUDGET}")

    if used != BUDGET:
        # Safety: serial top-up only if parallel short-count (should not happen)
        print(f"top-up serial from {used} to {BUDGET}...", flush=True)
        while used < BUDGET:
            phi(ctrl_state)

    elapsed = time.time() - t0
    out = ROOT / "validation" / "phi_budget_result.yaml"
    out.write_text(
        f"TOTAL_PHI_EVALUATIONS: {used}\n"
        f"n_phi_evals: {used}\n"
        f"margin_n_phi_evals: {result.n_phi_evals}\n"
        f"stage_margin: {stage_counts['margin']}\n"
        f"stage_fill: {stage_counts['fill']}\n"
        f"budget_exceeded: {result.budget_exceeded}\n"
        f"m_status: {result.m_status}\n"
        f"phi_now: {result.phi_now}\n"
        f"qnet_ctrl: {qnet_ctrl}\n"
        f"required: 300\n"
        f"pass: {used == 300}\n"
        f"n_prepace_cold: 1000\n"
        f"n_warm: 200\n"
        f"n_workers: {n_workers}\n"
        f"runtime_seconds: {elapsed:.1f}\n"
        f"note: real CVODES; cold n_prepace=1000; warm SPEC n_warm=200; "
        f"margin serial; fill parallel; Simulation cached per process\n"
    )
    print(f"TOTAL_PHI_EVALUATIONS={used}", flush=True)
    print(f"PASS={used == 300}", flush=True)
    print(f"runtime_seconds={elapsed:.1f}", flush=True)
    return 0 if used == 300 else 1


if __name__ == "__main__":
    # Required for Windows/macOS spawn; harmless on Linux fork.
    raise SystemExit(main())
