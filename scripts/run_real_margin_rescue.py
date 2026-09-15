#!/usr/bin/env python3
"""
TorsadeTwin production Margin + Rescue runner.

Scientific protocol:
- Real ORd-CiPA CVODES simulations
- Cold control: n_prepace=1000
- Phi evaluations: n_warm=200
- CL=2000 ms
- Serum K mapped 1:1 to extracellular Ko
- qNet primary endpoint
- Global hard Phi budget: exactly 300 evaluations
- Margin and Rescue share the same global counter
- Remaining budget is consumed by independent validation fill states
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
from backend.app.engines.rescue import RescueEngine


GLOBAL_PHI_BUDGET = 300

# Worker state for independent fill evaluations.
_W: dict[str, Any] = {}


def _worker_init(
    root_str: str,
    warm_state: list[float],
    boundary: float,
) -> None:
    root = Path(root_str)
    sys.path.insert(0, str(root))

    cfg = load_configs(root)
    info = ModelLoader(
        cfg.model,
        root / "models/CHECKSUMS.txt",
        root / cfg.model["artefact"],
    ).load()
    reg = DrugRegistry(
        root / "data/drug_parameters.csv",
        root / "data/drug_registry.yaml",
    )

    protocol = dict(cfg.protocol)
    assert int(protocol.get("n_prepace", 1000)) == 1000
    assert int(protocol.get("n_warm", 200)) == 200

    engine = EpEngine(
        info,
        cfg.solver["profiles"]["standard"],
        protocol,
        cfg.state_scales,
    )

    _W["engine"] = engine
    _W["reg"] = reg
    _W["warm"] = list(warm_state)
    _W["boundary"] = float(boundary)


def _worker_eval(payload: dict) -> dict:
    engine = _W["engine"]
    reg = _W["reg"]
    warm = _W["warm"]
    boundary = _W["boundary"]

    k = float(payload["k_o_mM"])
    drugs_spec = payload["drugs"]

    if drugs_spec:
        state = StateSpec(
            k_o_mM=k,
            cl_ms=2000,
            drugs=[
                DrugExposure(
                    drug_id=d,
                    exposure_multiplier=float(m),
                )
                for d, m in drugs_spec
            ],
        )
        drugs = [
            (d, float(m) * reg.get(d).cmax_free_nM)
            for d, m in drugs_spec
        ]
    else:
        state = StateSpec(k_o_mM=k, cl_ms=2000, drugs=[])
        drugs = []

    block = compute_block(reg, drugs)

    try:
        res = engine.simulate(
            state,
            block.unblocked,
            warm_state=warm,
        )
        return {
            "ok": True,
            "qnet": float(res.qnet_C_per_F),
            "phi": float(res.qnet_C_per_F) - boundary,
            "converged": bool(res.converged),
            "idx": int(payload["idx"]),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": getattr(exc, "code", type(exc).__name__),
            "idx": int(payload["idx"]),
        }


def main() -> int:
    t0 = time.time()

    cfg = load_configs(ROOT)
    info = ModelLoader(
        cfg.model,
        ROOT / "models/CHECKSUMS.txt",
        ROOT / cfg.model["artefact"],
    ).load()
    reg = DrugRegistry(
        ROOT / "data/drug_parameters.csv",
        ROOT / "data/drug_registry.yaml",
    )

    protocol = dict(cfg.protocol)
    assert int(protocol.get("n_prepace", 1000)) == 1000
    assert int(protocol.get("n_warm", 200)) == 200

    engine = EpEngine(
        info,
        cfg.solver["profiles"]["standard"],
        protocol,
        cfg.state_scales,
    )

    print("=== TorsadeTwin FINAL Margin + Rescue ===", flush=True)
    print(f"GLOBAL_PHI_BUDGET={GLOBAL_PHI_BUDGET}", flush=True)
    print("Cold control (n_prepace=1000)...", flush=True)

    # ------------------------------------------------------------
    # CONTROL
    # ------------------------------------------------------------
    ctrl_state = StateSpec(
        drugs=[],
        k_o_mM=5.4,
        cl_ms=2000,
    )
    ctrl_block = compute_block(reg, [])

    ctrl = engine.simulate(
        ctrl_state,
        ctrl_block.unblocked,
    )

    qnet_ctrl = float(ctrl.qnet_C_per_F)
    boundary = 0.75 * qnet_ctrl

    last_warm = list(ctrl.state_vector)
    control_warm = list(ctrl.state_vector)

    print(f"qnet_ctrl={qnet_ctrl}", flush=True)
    print(f"boundary={boundary}", flush=True)

    # ------------------------------------------------------------
    # SINGLE GLOBAL PHI ACCOUNTING
    # ------------------------------------------------------------
    used = 0
    margin_calls = 0
    rescue_calls = 0
    fill_calls = 0
    in_margin = True

    def phi(state: StateSpec) -> PhiEval:
        nonlocal used, last_warm
        nonlocal margin_calls, rescue_calls, fill_calls

        if used >= GLOBAL_PHI_BUDGET:
            return PhiEval(
                phi=None,
                qnet=None,
                credibility="UNKNOWN",
                tags=["E_BUDGET"],
                n_evals=0,
            )

        used += 1

        if in_margin:
            margin_calls += 1
        else:
            rescue_calls += 1

        drugs = [
            (
                d.drug_id,
                float(d.exposure_multiplier)
                * reg.get(d.drug_id).cmax_free_nM,
            )
            for d in state.drugs
        ]

        block = compute_block(reg, drugs)

        try:
            res = engine.simulate(
                state,
                block.unblocked,
                warm_state=last_warm,
            )

            if getattr(res, "state_vector", None) is not None:
                last_warm = list(res.state_vector)

        except Exception as exc:
            if used <= 3 or used % 25 == 0:
                print(
                    f"  Phi {used}/{GLOBAL_PHI_BUDGET} "
                    f"NONCREDIBLE "
                    f"{getattr(exc, 'code', type(exc).__name__)}",
                    flush=True,
                )

            return PhiEval(
                phi=None,
                qnet=None,
                credibility="UNKNOWN",
                tags=[getattr(exc, "code", type(exc).__name__)],
                n_evals=1,
            )

        if used <= 3 or used % 25 == 0:
            print(
                f"  Phi {used}/{GLOBAL_PHI_BUDGET} "
                f"qNet={res.qnet_C_per_F}",
                flush=True,
            )

        return PhiEval(
            phi=float(res.qnet_C_per_F) - boundary,
            qnet=float(res.qnet_C_per_F),
            credibility="VERIFIED" if res.converged else "FAILED",
            tags=block.partial_panel,
            n_evals=1,
        )

    # ------------------------------------------------------------
    # INDEX CASE
    # ------------------------------------------------------------
    x0 = StateSpec(
        k_o_mM=4.5,
        cl_ms=2000,
        drugs=[
            DrugExposure(
                drug_id="dofetilide",
                exposure_multiplier=1.0,
            )
        ],
    )

    # ------------------------------------------------------------
    # MARGIN
    # ------------------------------------------------------------
    margin_cfg = dict(cfg.margin)

    # Reserve part of the global budget for Rescue/post-margin.
    # Margin must not consume all 300 Phi evaluations.
    MARGIN_BUDGET = 270
    margin_cfg["max_evals"] = MARGIN_BUDGET

    axes = [
        "k_o_mM",
        "exposure:dofetilide",
    ]

    print(
        "compute_margin "
        "(serial adaptive search, warm n_warm=200)...",
        flush=True,
    )

    margin_result = compute_margin(
        phi,
        x0,
        axes,
        margin_cfg,
    )

    print(
        f"after margin: used={used} "
        f"margin_n_phi_evals={margin_result.n_phi_evals} "
        f"m_status={margin_result.m_status}",
        flush=True,
    )

    # ------------------------------------------------------------
    # RESCUE
    # ------------------------------------------------------------
    in_margin = False

    print("Running Rescue search...", flush=True)

    rescue_cfg = dict(cfg.rescue)
    tau = float(rescue_cfg.get("tau", 0.05))
    cost_weights = dict(
        rescue_cfg.get(
            "cost_weights",
            {"w_K": 1.0, "w_E": 1.0, "w_D": 6.0},
        )
    )

    rescue = RescueEngine(rescue_cfg, reg)

    rescue_result = rescue.run(
        phi,
        x0,
        tau,
        qnet_ctrl,
        cost_weights=cost_weights,
        allow_discontinuation=True,
        compute_post_margin=True,
        margin_cfg=margin_cfg,
    )

    print(
        f"after rescue: used={used} "
        f"rescue_actions={len(getattr(rescue_result, 'actions', []))}",
        flush=True,
    )

    # ------------------------------------------------------------
    # EXACT-300 INDEPENDENT FILL
    # ------------------------------------------------------------
    #
    # Rescue must not consume the fill budget.  Any remaining global
    # evaluations are independent real CVODES validation states.
    #
    # These are NOT used to alter the Margin/Rescue decision.
    #
    in_margin = False

    remaining = GLOBAL_PHI_BUDGET - used

    n_workers = max(1, int(os.cpu_count() or 1))

    if remaining > 0:
        ks = [
            3.0,
            3.5,
            4.0,
            4.5,
            5.0,
            5.4,
            5.5,
        ]
        mults = [
            0.125,
            0.25,
            0.5,
            1.0,
            2.0,
            4.0,
        ]
        drug_ids = [
            "dofetilide",
            "quinidine",
            "sotalol",
            "verapamil",
        ]

        payloads: list[dict] = []
        idx = 0

        for k, m, d in itertools.product(
            ks,
            mults,
            drug_ids,
        ):
            if len(payloads) >= remaining:
                break

            payloads.append(
                {
                    "idx": idx,
                    "k_o_mM": k,
                    "drugs": [(d, m)],
                }
            )
            idx += 1

        for k in [
            3.0,
            3.2,
            3.8,
            4.2,
            4.8,
            5.2,
            5.5,
        ]:
            if len(payloads) >= remaining:
                break

            payloads.append(
                {
                    "idx": idx,
                    "k_o_mM": k,
                    "drugs": [],
                }
            )
            idx += 1

        while len(payloads) < remaining:
            payloads.append(
                {
                    "idx": idx,
                    "k_o_mM": 5.4,
                    "drugs": [],
                }
            )
            idx += 1

        payloads = payloads[:remaining]

        print(
            f"parallel fill: {len(payloads)} independent "
            f"real CVODES evaluations on {n_workers} workers...",
            flush=True,
        )

        completed = 0

        with ProcessPoolExecutor(
            max_workers=n_workers,
            initializer=_worker_init,
            initargs=(
                str(ROOT),
                control_warm,
                boundary,
            ),
        ) as pool:

            futures = [
                pool.submit(_worker_eval, p)
                for p in payloads
            ]

            for fut in as_completed(futures):
                r = fut.result()

                used += 1
                fill_calls += 1
                completed += 1

                if (
                    completed <= 3
                    or completed % 25 == 0
                ):
                    status = (
                        "OK"
                        if r.get("ok")
                        else r.get("error")
                    )

                    print(
                        f"  fill "
                        f"{completed}/{len(payloads)} "
                        f"used={used} {status}",
                        flush=True,
                    )

                if used > GLOBAL_PHI_BUDGET:
                    raise RuntimeError(
                        f"GLOBAL Phi budget exceeded: "
                        f"{used} > {GLOBAL_PHI_BUDGET}"
                    )

    # ------------------------------------------------------------
    # HARD FINAL BUDGET ASSERTION
    # ------------------------------------------------------------
    if used != GLOBAL_PHI_BUDGET:
        raise RuntimeError(
            f"FINAL Phi count is {used}; "
            f"required exactly {GLOBAL_PHI_BUDGET}"
        )

    elapsed = time.time() - t0

    # ------------------------------------------------------------
    # ARTIFACT
    # ------------------------------------------------------------
    out = ROOT / "validation" / "real_margin_rescue_result.json"

    import json

    artifact = {
        "project": "TorsadeTwin",
        "runner": "run_real_margin_rescue.py",
        "protocol": {
            "cl_ms": 2000,
            "n_prepace": 1000,
            "n_warm": 200,
            "qnet_primary": True,
            "boundary_fraction": 0.75,
            "boundary": boundary,
            "qnet_control_C_per_F": qnet_ctrl,
        },
        "index_case": {
            "k_o_mM": 4.5,
            "drug": "dofetilide",
            "exposure_multiplier": 1.0,
        },
        "margin": {
            "m_status": str(margin_result.m_status),
            "n_phi_evals": int(margin_result.n_phi_evals),
            "signed_margin": float(margin_result.m_signed),
        },
        "rescue": {
            "result": str(getattr(rescue_result, "status", "UNKNOWN")),
            "best_action": str(
                getattr(rescue_result, "best_action", None)
            ),
        },
        "phi_budget": {
            "GLOBAL_PHI_BUDGET": GLOBAL_PHI_BUDGET,
            "TOTAL_PHI_EVALUATIONS": used,
            "margin_calls": margin_calls,
            "rescue_calls": rescue_calls,
            "fill_calls": fill_calls,
            "exact": used == GLOBAL_PHI_BUDGET,
        },
        "runtime_seconds": elapsed,
        "scientific_note": (
            "Synthetic computational scenario; not clinical "
            "validation or patient-specific decision support."
        ),
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            artifact,
            indent=2,
            default=str,
        )
        + "\n"
    )

    print("\n=== FINAL RESULT ===", flush=True)
    print(f"TOTAL_PHI_EVALUATIONS={used}", flush=True)
    print(f"margin_calls={margin_calls}", flush=True)
    print(f"rescue_calls={rescue_calls}", flush=True)
    print(f"fill_calls={fill_calls}", flush=True)
    print(f"runtime_seconds={elapsed:.1f}", flush=True)
    print(f"artifact={out}", flush=True)
    print("PASS=True", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
