from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.config import load_configs
from backend.app.engines.phi import ModelPhiEvaluator
from backend.app.ep.model_loader import ModelLoader
from backend.app.ep.simulate import EpEngine
from backend.app.main import create_app
from backend.app.schemas.common import StateSpec


ROOT = Path(__file__).resolve().parents[2]
CONTROL = {"drugs": [], "k_o_mM": 5.4, "cl_ms": 2000}


def test_real_control_simulation_and_data_gated_api_e2e():
    client = TestClient(create_app(ROOT))
    simulation = client.post("/api/v1/simulate", json={**CONTROL, "return_trace": False})
    assert simulation.status_code == 200
    payload = simulation.json()
    assert payload["qnet_C_per_F"] > 0
    assert payload["apd90_ms"] is not None
    assert payload["convergence"] == {"beats_run": 1001, "c1": True, "c2": True, "c3": True, "c4": True}
    assert payload["credibility"]["state"] == "UNVERIFIED"

    rescue = client.post("/api/v1/rescue", json={**CONTROL, "compute_post_margin": False})
    assert rescue.status_code == 200
    assert rescue.json()["execution_path"] == "DATA_GATED_DEMONSTRATION"
    assert rescue.json()["data_status"] == "SYNTHETIC_CONTROL_NO_PHARMACOLOGY"
    assert rescue.json()["status"] == "FEASIBLE"

    audit = client.post("/api/v1/blindspot", json={"base_state": CONTROL, "sweep": {"variable": "k_o_mM", "from": 5.4, "to": 5.0, "n_points": 3}})
    assert audit.status_code == 200
    assert audit.json()["status"] == "DATA_GATED_UNAVAILABLE"
    assert audit.json()["audit_status"] == "UNKNOWN"

    report = client.post("/api/v1/report", json={"state": CONTROL, "format": ["json"]})
    assert report.status_code == 200
    assert report.json()["json"]["data_status"] == "SYNTHETIC_CONTROL_NO_PHARMACOLOGY"
    assert report.json()["json"]["provenance"]["pharmacology"] == "NOT_USED"


def test_real_non_upstroke_is_unknown_not_a_phi_value():
    cfg = load_configs(ROOT)
    info = ModelLoader(cfg.model, ROOT / "models" / "CHECKSUMS.txt", ROOT / cfg.model["artefact"]).load()
    engine = EpEngine(info, cfg.solver["profiles"]["standard"], cfg.protocol, cfg.state_scales)
    evaluation = ModelPhiEvaluator(engine, None, float(cfg.thresholds["rho"]))(StateSpec(drugs=[], k_o_mM=3.0, cl_ms=2000))
    assert evaluation.credibility == "UNKNOWN"
    assert evaluation.phi is None
    assert "E_NO_UPSTROKE" in evaluation.tags


def test_unverified_drug_is_refused_from_verified_path():
    client = TestClient(create_app(ROOT))
    response = client.post("/api/v1/margin", json={
        "drugs": [{"drug_id": "dofetilide", "exposure_multiplier": 1.0}],
        "k_o_mM": 5.4,
        "cl_ms": 2000,
        "max_evals": 300,
    })
    assert response.status_code == 503
    assert response.json()["error_code"] == "E_PROVENANCE_INCOMPLETE"
