# Verify request/response (§20.6).
from __future__ import annotations

from pydantic import BaseModel, Field

from .simulate import SimulateRequest


class VerifyRequest(BaseModel):
    scope: str = "request"  # "request" | "battery_lookup"
    state: SimulateRequest | None = None


class CheckResult(BaseModel):
    id: str
    name: str
    tier: str
    state: str  # PASS | FAIL | UNKNOWN
    detail: str = ""
    threshold: str = ""
    observed: str = ""


class VerifyResponse(BaseModel):
    checks: list[CheckResult]
    aggregate: str
    battery: dict | None = None
