# Margin request/response (§20.3).
from __future__ import annotations

from pydantic import BaseModel, Field

from .simulate import SimulateRequest


class MarginRequest(SimulateRequest):
    axes: list[str] = Field(default_factory=list)  # e.g. ["k_o_mM", "exposure:dofetilide"]
    weights: dict[str, float] = Field(default_factory=dict)
    box_override: dict | None = None
    max_evals: int = 300


class AxisResult(BaseModel):
    axis: str
    distance: float | None
    critical_raw_value: float | None
    direction: str | None
    monotonicity: str = "MONOTONIC"
    all_roots: list[float] = Field(default_factory=list)
    reachable: bool = False
    sensitivity_share: float | None = None


class BindingConstraint(BaseModel):
    axis: str | None
    critical_raw_value: float | None
    tied_axes: list[str] = Field(default_factory=list)
    alternative_axis: str | None = None
    alternative_critical_value: float | None = None
    distance_vs_sensitivity_disagree: bool = False


class MarginResponse(BaseModel):
    phi_now: float
    m_signed: float | None
    m_status: str
    m_label: str = ""
    axes: list[AxisResult] = Field(default_factory=list)
    binding_constraint: BindingConstraint
    n_phi_evals: int = 0
    unit_convention: str = "1 normalised unit = 1 mM K+ = one doubling of exposure"
    credibility: dict
    disclaimers: list[str] = Field(default_factory=list)
