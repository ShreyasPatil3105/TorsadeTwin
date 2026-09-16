from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.schemas.llm import LLMExplainRequest
from backend.app.services.errors import TorsadeTwinError
from backend.app.services.groq_llm import explain


def test_llm_endpoint_requires_server_side_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(TorsadeTwinError) as error:
        explain("What does qNet represent?")

    assert error.value.code == "E_LLM_NOT_CONFIGURED"


def test_llm_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        LLMExplainRequest(question="Explain this.", api_key="must-not-be-client-supplied")
