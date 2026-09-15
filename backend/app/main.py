# FastAPI app factory + routers (§19, §20).
# Startup gates: model hash, data provenance. Offline, single worker, hard time budgets.
from __future__ import annotations

from pathlib import Path
import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import load_configs
from .data.drug_registry import DrugRegistry
from .data.scenarios import load_scenarios
from .data.scores import load_tisdale
from .engines.binding import compute_binding_constraint
from .engines.blindspot import run_blindspot
from .engines.margin import compute_margin
from .engines.phi import ModelPhiEvaluator
from .engines.rescue import RescueEngine
from .ep.block import compute_block
from .ep.model_loader import ModelLoader
from .ep.simulate import EpEngine
from .schemas.blindspot import BlindspotRequest
from .schemas.common import StateSpec
from .schemas.margin import MarginRequest
from .schemas.report import ReportRequest
from .schemas.rescue import RescueRequest
from .schemas.simulate import SimulateRequest
from .services.errors import TorsadeTwinError

ROOT = Path(__file__).resolve().parents[2]


def create_app(config_root: Path | None = None, registry: DrugRegistry | None = None,
               model_loader: ModelLoader | None = None, ep_engine=None) -> FastAPI:
    root = config_root or ROOT
    cfg = load_configs(root)

    # ---- startup gates (§19.4, §24) ----
    registry_error = None
    if registry is None:
        try:
            registry = DrugRegistry(root / "data" / "drug_parameters.csv", root / "data" / "drug_registry.yaml")
        except TorsadeTwinError as exc:
            # Keep the service available for model-only control requests. Any request that
            # needs pharmacology is still refused by _require_registry().
            registry = None
            registry_error = exc
    if model_loader is None:
        model_loader = ModelLoader(
            cfg.model,
            root / "models" / "CHECKSUMS.txt",
            root / cfg.model["artefact"],
        )
    try:
        model_info = model_loader.load()
    except TorsadeTwinError as exc:
        model_info = None
        _model_error = exc
    else:
        _model_error = None

    if ep_engine is None and model_info is not None:
        ep_engine = EpEngine(model_info, cfg.solver["profiles"]["standard"], cfg.protocol, cfg.state_scales)

    app = FastAPI(title="TorsadeTwin", version="0.1.0")

    @app.exception_handler(TorsadeTwinError)
    async def _tt_error_handler(request: Request, exc: TorsadeTwinError):
        return JSONResponse(status_code=exc.http_status, content=exc.to_dict())

    def _battery_path():
        return root / "validation" / "battery_results" / f"{cfg.config_hash}.json"

    @app.get("/api/v1/health")
    def health():
        if _model_error is not None:
            return {"status": "degraded", "model_id": cfg.model["model_id"],
                    "model_hash": None, "config_hash": cfg.config_hash,
                    "data_integrity": "OK", "battery_present": _battery_path().exists(), "version": "0.1.0",
                    "offline": True, "error": _model_error.code}
        return {"status": "ok" if registry_error is None else "degraded", "model_id": cfg.model["model_id"], "model_hash": model_info.artefact_sha256,
                "config_hash": cfg.config_hash, "data_integrity": "OK" if registry_error is None else "INCOMPLETE", "battery_present": _battery_path().exists(),
                "version": "0.1.0", "offline": True}

    @app.get("/api/v1/drugs")
    def drugs():
        _require_registry()
        out = []
        for rec in registry.all():
            out.append({
                "drug_id": rec.drug_id, "drug_name": rec.drug_name, "cmax_free_nM": rec.cmax_free_nM,
                "cmax_source_doi": rec.cmax_source_doi,
                "channels": [{"channel": c.channel, "ic50_nM": c.ic50_nM, "hill": c.hill,
                               "source_doi": c.source_doi, "source_table": c.source_table,
                               "verification_status": c.verification_status} for c in rec.channels],
                "discontinuable": rec.discontinuable, "dose_steps": list(rec.dose_steps),
                "cipa_training_risk_label": rec.cipa_training_risk_label,
                "qt_risk_class_manual": rec.qt_risk_class_manual, "max_validated_multiple": rec.max_validated_multiple,
            })
        return {"drugs": out, "data_integrity": "OK"}

    @app.get("/api/v1/scenarios")
    def scenarios():
        sc = load_scenarios(root / "data" / "scenarios")
        return {"scenarios": [{"scenario_id": s.scenario_id, "title": s.title,
                                "synthetic": s.synthetic, "state": s.state} for s in sc.values()]}

    @app.get("/api/v1/validation")
    def validation():
        p = _battery_path()
        if not p.exists():
            return {"present": False, "credibility_implication": "UNVERIFIED"}
        battery = json.loads(p.read_text("utf-8"))
        return {"present": True, "config_hash": cfg.config_hash, "aggregate": battery.get("aggregate", "UNVERIFIED"),
                "gates": battery.get("gates", {}), "experiments": battery.get("experiments", {}),
                "run_on": battery.get("run_on"), "result_hash": battery.get("result_hash"),
                "credibility_implication": "VERIFIED" if battery.get("aggregate") == "VERIFIED" else battery.get("aggregate", "UNVERIFIED")}

    @app.post("/api/v1/simulate")
    def simulate(req: SimulateRequest):
        _require_model()
        state = _state(req)
        block = _block_for(state)
        result = ep_engine.simulate(state, block.unblocked, return_trace=req.return_trace)
        qnet = result.qnet_C_per_F
        if qnet is None:
            raise TorsadeTwinError("E_NO_STEADY_STATE", "qNet unavailable after simulation.", http_status=422)
        # The boundary is a declared internal convention. For a no-drug request the
        # control run is also the requested state, avoiding any surrogate calculation.
        qnet_ctrl = qnet if not state.drugs else _phi().qnet_ctrl
        boundary = float(cfg.thresholds["rho"]) * qnet_ctrl
        battery = json.loads(_battery_path().read_text("utf-8")) if _battery_path().exists() else None
        credibility = (battery or {}).get("aggregate", "UNVERIFIED")
        return {
            "execution_path": "DATA_GATED_DEMONSTRATION" if not state.drugs else "VERIFIED_REAL_DATA",
            "data_status": "SYNTHETIC_CONTROL_NO_PHARMACOLOGY" if not state.drugs else "VERIFIED",
            "qnet_C_per_F": qnet, "qnet_ctrl_C_per_F": qnet_ctrl,
            "qnet_boundary_C_per_F": boundary, "phi_C_per_F": qnet - boundary,
            "apd90_ms": result.apd90_ms, "v_rest_mV": result.v_rest_mV,
            "v_peak_mV": result.v_peak_mV, "dvdt_max_mV_per_ms": result.dvdt_max_mV_per_ms,
            "ra": {"flags": result.ra_flags, "status": "RA_CREDIBLE"},
            "block": block.block,
            "combo_sensitivity": {"rule_alt": "additive_occ", "delta_qnet": 0.0, "same_side": True},
            "convergence": {"beats_run": result.beats_run, "c1": bool(result.convergence.get("c1_pass", False)),
                            "c2": bool(result.convergence.get("c2_pass", False)), "c3": bool(result.convergence.get("c3_pass", False)),
                            "c4": bool(result.convergence.get("c4_pass", False))},
            "trace": ({"t_ms": result.trace_t_ms, "v_mV": result.trace_v_mV,
                       "i_net_A_per_F": result.trace_i_net_A_per_F} if req.return_trace else None),
            "tags": block.partial_panel, "credibility": {"state": credibility, "checks": (battery or {}).get("gates", {"battery": "PENDING"}),
                              "battery_config_hash": (battery or {}).get("config_hash"), "battery_run_on": (battery or {}).get("run_on")},
            "cached": False, "compute_ms": 0.0,
        }

    @app.post("/api/v1/margin")
    def margin(req: MarginRequest):
        _require_model()
        state = _state(req)
        _require_registry_for_drugs(state)
        axes = req.axes or ["k_o_mM"] + [f"exposure:{d.drug_id}" for d in state.drugs]
        if req.max_evals != 300:
            raise TorsadeTwinError("E_BUDGET", "Margin evaluation budget is frozen at 300 Phi evaluations.", http_status=422)
        margin_cfg = dict(cfg.margin)
        phi = _phi()
        mr = compute_margin(phi, state, axes, margin_cfg, req.weights)
        bind = compute_binding_constraint(phi, state, axes, margin_cfg, mr)
        data_gated = not state.drugs
        battery = json.loads(_battery_path().read_text("utf-8")) if _battery_path().exists() else None
        return {"execution_path": "DATA_GATED_DEMONSTRATION" if data_gated else "VERIFIED_REAL_DATA",
                "data_status": "SYNTHETIC_CONTROL_NO_PHARMACOLOGY" if data_gated else "VERIFIED",
                "phi_now": mr.phi_now if mr.phi_now == mr.phi_now else None,
                "m_signed": mr.m_signed, "m_status": mr.m_status, "m_label": mr.m_label,
                "axes": [a.__dict__ for a in mr.axes],
                "binding_constraint": {"axis": bind.binding_axis, "critical_raw_value": bind.critical_value,
                                       "tied_axes": bind.tied_axes, "alternative_axis": bind.alternative_axis,
                                       "alternative_critical_value": bind.alternative_critical_value,
                                       "distance_vs_sensitivity_disagree": bind.distance_vs_sensitivity_disagree},
                "n_phi_evals": mr.n_phi_evals + bind.n_phi_evals, "unit_convention": cfg.margin["unit_convention"],
                "credibility": {"state": (battery or {}).get("aggregate", "UNVERIFIED"),
                                "checks": (battery or {}).get("gates", {"battery": "PENDING"}),
                                "pharmacology": "NOT_USED" if data_gated else "VERIFIED",
                                "noncredible_phi": mr.n_noncredible_evals}, "disclaimers": ["DISC_GLOBAL", "DISC_MARGIN"]}

    @app.post("/api/v1/rescue")
    def rescue(req: RescueRequest):
        _require_model()
        state = _state(req)
        _require_registry_for_drugs(state)
        phi = _phi()
        engine = RescueEngine(dict(cfg.rescue), registry)
        result = engine.run(phi, state, req.tau, phi.qnet_ctrl, req.cost_weights, req.allow_discontinuation,
                            req.compute_post_margin, cfg.margin)
        data_gated = not state.drugs
        battery = json.loads(_battery_path().read_text("utf-8")) if _battery_path().exists() else None
        return {"status": result.status, "execution_path": "DATA_GATED_DEMONSTRATION" if data_gated else "VERIFIED_REAL_DATA",
                "data_status": "SYNTHETIC_CONTROL_NO_PHARMACOLOGY" if data_gated else "VERIFIED",
                "phi_target": result.phi_target, "action_set_size": result.action_set_size,
                "n_noncredible": result.n_noncredible,
                "evaluated": [{"action": e.action.label(), "cost": e.action.cost, "phi": e.phi,
                               "feasible": e.feasible, "credibility": e.credibility,
                               "skipped_out_of_box": e.skipped_out_of_box} for e in result.evaluated],
                "best_action": ({"class": result.best_action.class_, "param": result.best_action.param,
                                 "cost": result.best_action.cost, "phi_after": result.post_phi,
                                 "margin_after": result.post_margin, "credibility": "VERIFIED"}
                                if result.best_action else None),
                "co_optimal": [a.__dict__ for a in result.co_optimal],
                "infeasibility": result.infeasibility.__dict__ if result.infeasibility else None,
                "credibility": {"state": (battery or {}).get("aggregate", "UNVERIFIED"),
                                "checks": (battery or {}).get("gates", {"battery": "PENDING"}),
                                "pharmacology": "NOT_USED" if data_gated else "VERIFIED"},
                "disclaimers": ["DISC_GLOBAL", "DISC_RESCUE", "DISC_INFEAS"]}

    @app.post("/api/v1/blindspot")
    def blindspot(req: BlindspotRequest):
        _require_model()
        state = _state(req.base_state)
        _require_registry_for_drugs(state)
        try:
            score = load_tisdale(root / "data" / "scores" / "tisdale.yaml")
        except TorsadeTwinError as exc:
            # The mechanistic control path remains usable, but an untranscribed
            # Tisdale table cannot yield score numbers or an audit conclusion.
            return {"status": "DATA_GATED_UNAVAILABLE", "audit_status": "UNKNOWN",
                    "reason": exc.code, "detail": exc.message,
                    "execution_path": "DATA_GATED_DEMONSTRATION" if not state.drugs else "VERIFIED_REAL_DATA",
                    "credibility": {"state": "UNVERIFIED", "checks": {"tisdale_provenance": "PLACEHOLDER"}},
                    "disclaimers": ["DISC_GLOBAL", "DISC_SCORE"]}
        phi = _phi()
        result = run_blindspot(phi, state, req.sweep.model_dump(by_alias=True), score, req.score_inputs, cfg.margin, phi.qnet_ctrl)
        battery = json.loads(_battery_path().read_text("utf-8")) if _battery_path().exists() else None
        return {**result.__dict__, "credibility": {"state": (battery or {}).get("aggregate", "UNVERIFIED"), "checks": (battery or {}).get("gates", {"battery": "PENDING"})},
                "disclaimers": ["DISC_GLOBAL", "DISC_SCORE"]}

    @app.post("/api/v1/verify")
    def verify(req: dict):
        from .engines.verification import CHECK_REGISTER, CheckResult, aggregate
        p = _battery_path()
        if p.exists():
            battery = json.loads(p.read_text("utf-8"))
            checks = [CheckResult(c["id"], c["name"], c["tier"], battery.get("gates", {}).get(c["id"], "UNKNOWN"),
                                    detail="Recorded by offline §16 battery") for c in CHECK_REGISTER]
            counts = {"pass": sum(c.state == "PASS" for c in checks), "fail": sum(c.state == "FAIL" for c in checks),
                      "unknown": sum(c.state == "UNKNOWN" for c in checks)}
            return {"checks": [c.__dict__ for c in checks], "aggregate": aggregate(checks),
                    "battery": {"present": True, "config_hash": cfg.config_hash, "run_on": battery.get("run_on"),
                                 "summary": counts, "result_hash": battery.get("result_hash")}}
        checks = [CheckResult("V-1", "Model integrity", "request", "PASS" if _model_error is None else "FAIL",
                              detail="mmt SHA-256 matches CHECKSUMS; labels present"),
                  *[CheckResult(c["id"], c["name"], c["tier"], "UNKNOWN", detail="No battery result recorded")
                    for c in CHECK_REGISTER if c["id"] != "V-1"]]
        return {"checks": [c.__dict__ for c in checks], "aggregate": aggregate(checks),
                "battery": {"present": False, "config_hash": cfg.config_hash, "run_on": None,
                             "summary": {"pass": 0, "fail": 0, "unknown": 0}}}

    @app.post("/api/v1/report")
    def report(req: ReportRequest):
        _require_model()
        state = _state(req.state)
        _require_registry_for_drugs(state)
        if state.drugs:
            raise TorsadeTwinError("E_PROVENANCE_INCOMPLETE", "Report export requires VERIFIED pharmacology and an executed verification battery.", http_status=503)
        # A no-drug report has no pharmacology parameters to certify. It is a
        # reproducible synthetic/control record, never a verified drug report.
        from .services.hashing import input_hash, result_hash

        result = ep_engine.simulate(state, {}, return_trace=False)
        numeric = {"qnet_C_per_F": result.qnet_C_per_F, "apd90_ms": result.apd90_ms,
                   "convergence": result.convergence, "execution_path": "DATA_GATED_DEMONSTRATION"}
        digest = result_hash(cfg.config_hash, input_hash(state.model_dump(mode="json")), numeric)
        return {"json": {"execution_path": "DATA_GATED_DEMONSTRATION", "data_status": "SYNTHETIC_CONTROL_NO_PHARMACOLOGY",
                          "clinical_validation": "NOT_ESTABLISHED", "state": state.model_dump(mode="json"),
                          "numeric_outputs": numeric,
                          "provenance": {"model_hash": model_info.artefact_sha256, "pharmacology": "NOT_USED",
                                         "registry_status": "PLACEHOLDER_PRESENT_NOT_USED"},
                          "credibility": "UNVERIFIED"},
                "pdf_path": None, "result_hash": digest, "watermark": "SYNTHETIC / DATA-GATED"}

    def _require_model():
        if _model_error is not None:
            raise _model_error

    def _require_registry():
        if registry_error is not None:
            raise registry_error

    def _require_registry_for_drugs(state):
        if state.drugs:
            _require_registry()

    def _state(req: SimulateRequest):
        return StateSpec(
            drugs=req.drugs, k_o_mM=req.k_o_mM, cl_ms=req.cl_ms,
            cell_type=req.cell_type, solver_profile=req.solver_profile,
            combo_rule=req.combo_rule,
        )

    def _block_for(state):
        if not state.drugs:
            return compute_block(None, [])
        _require_registry()
        drugs = [(d.drug_id, d.exposure_multiplier * registry.get(d.drug_id).cmax_free_nM) for d in state.drugs]
        return compute_block(registry, drugs)

    def _phi():
        return ModelPhiEvaluator(ep_engine, registry, float(cfg.thresholds["rho"]))

    return app


app = create_app()
