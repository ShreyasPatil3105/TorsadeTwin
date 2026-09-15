# Simulate request/response (§20.2).
from __future__ import annotations

from pydantic import BaseModel, Field

from .common import ComboRule, DrugExposure, SolverProfile


class SimulateRequest(BaseModel):
    model_config = {"extra": "forbid"}
    drugs: list[DrugExposure] = Field(default_factory=list, max_length=4)
    k_o_mM: float = Field(default=5.4, ge=2.5, le=7.0)
    cl_ms: int = Field(default=2000, ge=500, le=2000)
    cell_type: str = "endo"
    solver_profile: SolverProfile = SolverProfile.standard
    return_trace: bool = False
    combo_rule: ComboRule = ComboRule.indep_mult


class RaInfo(BaseModel):
    flags: list[str] = Field(default_factory=list)
    status: str = "RA_CREDIBLE"


class ComboSensitivity(BaseModel):
    rule_alt: str = "additive_occ"
    delta_qnet: float = 0.0
    same_side: bool = True


class Convergence(BaseModel):
    beats_run: int = 0
    c1: bool = False
    c2: bool = False
    c3: bool = False
    c4: bool = False


class SimulateResponse(BaseModel):
    qnet_C_per_F: float
    qnet_ctrl_C_per_F: float
    qnet_boundary_C_per_F: float
    phi_C_per_F: float
    apd90_ms: float | None
    v_rest_mV: float | None = None
    v_peak_mV: float | None = None
    dvdt_max_mV_per_ms: float | None = None
    ra: RaInfo
    block: dict[str, float]
    combo_sensitivity: ComboSensitivity
    convergence: Convergence
    trace: dict | None = None
    tags: list[str] = Field(default_factory=list)
    credibility: dict
    cached: bool = False
    compute_ms: float = 0.0
