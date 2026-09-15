# Blind-spot request/response (§20.5).
from __future__ import annotations

from pydantic import BaseModel, Field

from .simulate import SimulateRequest


class SweepSpec(BaseModel):
    variable: str  # "k_o_mM" or "exposure:<drug_id>"
    from_: float = Field(alias="from")
    to: float
    n_points: int = 21

    model_config = {"populate_by_name": True}


class BlindspotRequest(BaseModel):
    model_config = {"extra": "forbid"}
    base_state: SimulateRequest
    sweep: SweepSpec
    score_inputs: dict = Field(default_factory=dict)


class InsensitivityInterval(BaseModel):
    from_: float = Field(alias="from")
    to: float
    band: str
    delta_phi: float

    model_config = {"populate_by_name": True}


class BlindspotResponse(BaseModel):
    grid: list[float]
    phi: list[float]
    margin: list[float | None]
    score_min: list[int]
    score_max: list[int]
    score_band: list[str]
    insensitivity_intervals: list[InsensitivityInterval]
    crossing_point: float | None = None
    verdict: str
    assumptions: list[str] = Field(default_factory=list)
    credibility: dict
    disclaimers: list[str] = Field(default_factory=list)
