# Rescue request/response (§11.7, §12.3, §20.4).
from __future__ import annotations

from pydantic import BaseModel, Field

from .simulate import SimulateRequest


class RescueRequest(SimulateRequest):
    tau: float = 0.05
    cost_weights: dict[str, float] = Field(default_factory=lambda: {"w_K": 1.0, "w_E": 1.0, "w_D": 6.0})
    allow_discontinuation: bool = True
    compute_post_margin: bool = True


class ActionParam(BaseModel):
    k_o_mM: float | None = None
    drug: str | None = None
    factor: float | None = None


class EvaluatedAction(BaseModel):
    action: str
    cost: float
    phi: float
    feasible: bool
    credibility: str
    skipped_out_of_box: bool = False


class BestAction(BaseModel):
    class_: str = Field(alias="class")
    param: ActionParam
    cost: float
    phi_after: float
    margin_after: float | None = None
    credibility: str

    model_config = {"populate_by_name": True}


class InfeasibilityReport(BaseModel):
    reason_code: str
    explanation: str
    closest_action: dict
    shortfall_normalised: float | None = None
    limiting_bound: str = ""
    what_would_help: str = "Two-action combinations and drug substitution are outside the declared search scope."


class RescueResponse(BaseModel):
    status: str
    search_scope: str = "single_actions_only"
    phi_target: float
    best_action: BestAction | None = None
    co_optimal: list[dict] = Field(default_factory=list)
    evaluated: list[EvaluatedAction] = Field(default_factory=list)
    action_set_size: int = 0
    n_noncredible: int = 0
    infeasibility: InfeasibilityReport | None = None
    credibility: dict
    disclaimers: list[str] = Field(default_factory=list)
