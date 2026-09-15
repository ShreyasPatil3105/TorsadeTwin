#!/usr/bin/env python3
"""DEVELOPMENT_SMOKE — temporary real-CVODES Margin + Rescue runner.

Does NOT call POST /api/v1/margin (production requires max_evals==300).
Calls compute_margin() and RescueEngine.run() directly with DEV_MAX_EVALS=25.

Scientific settings unchanged:
  n_prepace=1000 cold control, n_warm=200 warm Phi, max_step=0.1,
  Stage B budget fix, max_evals_per_axis=30, real ORd-CiPA Myokit CVODES.
"""
from __future__ import annotations

from pathlib import Path
import sys
import time
import json
import os

os.environ["PYTHONUNBUFFERED"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import load_configs
from backend.app.ep.model_loader import ModelLoader
from backend.app.ep.simulate import EpEngine
from backend.app.data.drug_registry import DrugRegistry
from backend.app.schemas.common import StateSpec, DrugExposure
from backend.app.engines.phi import ModelPhiEvaluator, PhiEval
from backend.app.engines.margin import compute_margin
from backend.app.engines.rescue import RescueEngine

DEV_MAX_EVALS = 25  # development only; production API remains frozen at 300


def main() -> int:
    t0 = time.time()
    cfg = load_configs(ROOT)
    protocol = dict(cfg.protocol)
    assert int(protocol["n_prepace"]) == 1000, "n_prepace must be 1000"
    assert int(protocol["n_warm"]) == 200, "n_warm must be 200"

    info = ModelLoader(cfg.model, ROOT / "models/CHECKSUMS.txt", ROOT / cfg.model["artefact"]).load()
    reg = DrugRegistry(ROOT / "data/drug_parameters.csv", ROOT / "data/drug_registry.yaml")
    engine = EpEngine(info, cfg.solver["profiles"]["standard"], protocol, cfg.state_scales)
    base = ModelPhiEvaluator(engine, reg, rho=0.75)

    _orig = engine.simulate
    sim_log: list[dict] = []
    trace_path = ROOT / "validation" / "dev_smoke_sim_trace.log"
    trace_path.write_text("")  # reset

    def tracked(state, block_unblocked, return_trace=False, warm_state=None):
        mode = "WARM_n200" if warm_state is not None else "COLD_n1000"
        t1 = time.time()
        res = _orig(state, block_unblocked, return_trace=return_trace, warm_state=warm_state)
        entry = {
            "n": len(sim_log) + 1,
            "mode": mode,
            "dt_s": round(time.time() - t1, 2),
            "qnet": res.qnet_C_per_F,
            "apd90_ms": res.apd90_ms,
        }
        sim_log.append(entry)
        line = f"SIM#{entry['n']} {mode} dt={entry['dt_s']}s qNet={entry['qnet']}\n"
        print(line, end="", flush=True)
        with open(trace_path, "a") as f:
            f.write(line)
            f.flush()
        return res

    engine.simulate = tracked  # type: ignore

    print("=== DEVELOPMENT_SMOKE (NOT production 300-Phi validation) ===", flush=True)
    print("CONTROL cold n_prepace=1000...", flush=True)
    qnet_ctrl = float(base.qnet_ctrl)
    boundary = 0.75 * qnet_ctrl
    print(f"qnet_ctrl={qnet_ctrl}", flush=True)
    print(f"boundary={boundary}", flush=True)

    def phi(state: StateSpec) -> PhiEval:
        return base(state)

    x0 = StateSpec(
        k_o_mM=4.5,
        cl_ms=2000,
        drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)],
    )
    axes = ["exposure:dofetilide"]
    margin_cfg = dict(cfg.margin)
    margin_cfg["max_evals"] = DEV_MAX_EVALS  # local override only; configs/margin.yaml + API untouched

    print(f"MARGIN direct compute_margin axes={axes} max_evals={DEV_MAX_EVALS}", flush=True)
    mr = compute_margin(phi, x0, axes, margin_cfg)
    print(
        f"MARGIN status={mr.m_status} signed={mr.m_signed} phi_now={mr.phi_now} "
        f"n_phi_evals={mr.n_phi_evals} budget_exceeded={mr.budget_exceeded}",
        flush=True,
    )
    axes_out = [
        {
            "axis": a.axis,
            "distance": a.distance,
            "critical_raw_value": a.critical_raw_value,
            "reachable": a.reachable,
            "monotonicity": a.monotonicity,
        }
        for a in mr.axes
    ]
    for a in axes_out:
        print(f"  axis={a}", flush=True)

    # Production-equivalent RescueEngine.run() call (see backend/app/main.py + RescueRequest defaults).
    # tau=0.05 → Phi_target = tau * qNet_ctrl (configs/rescue.yaml / schema default).
    # compute_post_margin=True matches production; post-margin uses the same dev margin_cfg budget.
    print("RESCUE (production-equivalent signature)...", flush=True)
    cost_weights = {"w_K": 1.0, "w_E": 1.0, "w_D": 6.0}  # RescueRequest default
    allow_discontinuation = True  # RescueRequest default
    compute_post_margin = True  # RescueRequest / production default
    tau = float(cfg.rescue.get("tau", 0.05))  # production default 0.05
    rr = RescueEngine(dict(cfg.rescue), reg).run(
        phi,
        x0,
        tau,
        qnet_ctrl,
        cost_weights,
        allow_discontinuation,
        compute_post_margin,
        margin_cfg,
    )
    print(f"RESCUE status={rr.status}", flush=True)
    print(f"RESCUE best={rr.best_action.label() if rr.best_action else None}", flush=True)
    print(f"RESCUE post_phi={rr.post_phi}", flush=True)
    ev = [
        {
            "action": e.action.label(),
            "phi": e.phi,
            "feasible": e.feasible,
            "credibility": e.credibility,
        }
        for e in rr.evaluated
    ]
    for e in ev:
        print(f"  {e}", flush=True)

    warm_ok = all(s["mode"] == "WARM_n200" for s in sim_log[1:]) if len(sim_log) > 1 else False
    out = {
        "label": "DEVELOPMENT_SMOKE",
        "not_production_300_phi_validation": True,
        "production_api_max_evals_unchanged": 300,
        "dev_max_evals": DEV_MAX_EVALS,
        "qnet_ctrl": qnet_ctrl,
        "boundary": boundary,
        "sim_log": sim_log,
        "warm_from_sim2_onward": warm_ok,
        "margin": {
            "status": mr.m_status,
            "phi_now": mr.phi_now,
            "m_signed": mr.m_signed,
            "n_phi_evals": mr.n_phi_evals,
            "budget_exceeded": mr.budget_exceeded,
            "axes": axes_out,
        },
        "rescue": {
            "status": rr.status,
            "best_action": rr.best_action.label() if rr.best_action else None,
            "post_phi": rr.post_phi,
            "evaluated": ev,
            "n_noncredible": rr.n_noncredible,
        },
        "runtime_seconds": round(time.time() - t0, 1),
        "n_prepace": 1000,
        "n_warm": 200,
    }
    out_path = ROOT / "validation" / "dev_margin_rescue_smoke.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"wrote {out_path}", flush=True)
    print(f"warm_from_sim2_onward={warm_ok} runtime_seconds={out['runtime_seconds']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
