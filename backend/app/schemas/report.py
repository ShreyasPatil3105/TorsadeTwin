# Report request/response (§20.8).
from __future__ import annotations

from pydantic import BaseModel, Field

from .simulate import SimulateRequest


class ReportRequest(BaseModel):
    include: list[str] = Field(default_factory=list)
    state: SimulateRequest
    format: list[str] = Field(default_factory=lambda: ["json", "pdf"])
    result_hashes: list[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    json: dict
    pdf_path: str | None = None
    result_hash: str
    watermark: str = "NONE"
