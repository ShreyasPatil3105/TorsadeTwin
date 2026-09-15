# Common schemas: StateSpec, DrugExposure, SolverProfile, Credibility, Provenance (§2.2 L1, §18.2).
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SolverProfile(str, Enum):
    standard = "standard"
    tight = "tight"
    loose_NEGATIVE_CONTROL = "loose_NEGATIVE_CONTROL"
    coarse_log = "coarse_log"


class ComboRule(str, Enum):
    indep_mult = "indep_mult"
    additive_occ = "additive_occ"


class CellType(str, Enum):
    endo = "endo"


class DrugExposure(BaseModel):
    model_config = {"extra": "forbid"}
    drug_id: str
    exposure_multiplier: float = Field(ge=0.0, le=25.0)


class StateSpec(BaseModel):
    """Frozen input state (§2.2 L1)."""
    model_config = {"extra": "forbid"}
    drugs: list[DrugExposure] = Field(default_factory=list, max_length=4)
    k_o_mM: float = Field(default=5.4, ge=2.5, le=7.0)
    cl_ms: int = Field(default=2000, ge=500, le=2000)
    cell_type: CellType = CellType.endo
    solver_profile: SolverProfile = SolverProfile.standard
    combo_rule: ComboRule = ComboRule.indep_mult

    @field_validator("drugs")
    @classmethod
    def _unique_drugs(cls, v: list[DrugExposure]) -> list[DrugExposure]:
        ids = [d.drug_id for d in v]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate drug_id in drugs")
        return v

    def to_canonical(self) -> dict:
        return {
            "drugs": sorted(
                [{"drug_id": d.drug_id, "exposure_multiplier": d.exposure_multiplier} for d in self.drugs],
                key=lambda x: x["drug_id"],
            ),
            "k_o_mM": self.k_o_mM,
            "cl_ms": self.cl_ms,
            "cell_type": self.cell_type.value,
            "solver_profile": self.solver_profile.value,
            "combo_rule": self.combo_rule.value,
        }


class Credibility(BaseModel):
    state: str  # VERIFIED | UNVERIFIED | FAILED
    checks: dict[str, str] = Field(default_factory=dict)
    battery_config_hash: str | None = None
    battery_run_on: str | None = None
    n_noncredible_evals: int = 0


class Provenance(BaseModel):
    """Provenance record attached to every result (§18.2)."""
    software: dict
    model: dict
    solver: dict
    protocol: dict
    parameters: list[dict]
    assumptions: list[str]
    boundary: dict
    config_hash: str
    result_hash: str
    credibility: dict
    timestamp_utc: str
    disclaimers: list[str]
