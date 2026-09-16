from __future__ import annotations

from pydantic import BaseModel, Field


class LLMExplainRequest(BaseModel):
    model_config = {"extra": "forbid"}

    question: str = Field(min_length=1, max_length=2000)
    context: dict[str, object] | None = None


class LLMExplainResponse(BaseModel):
    answer: str
    model: str
    disclaimer: str