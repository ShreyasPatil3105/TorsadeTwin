from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import ROOT, create_app


def test_llm_endpoint_requires_server_side_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client = TestClient(create_app(ROOT))

    response = client.post(
        "/api/v1/llm/explain",
        json={"question": "What does qNet represent?"},
    )

    assert response.status_code == 503
    assert response.json()["error_code"] == "E_LLM_NOT_CONFIGURED"


def test_llm_request_rejects_unknown_fields(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client = TestClient(create_app(ROOT))

    response = client.post(
        "/api/v1/llm/explain",
        json={"question": "Explain this.", "api_key": "must-not-be-client-supplied"},
    )

    assert response.status_code == 422