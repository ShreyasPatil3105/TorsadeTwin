# L9 — Verification / credibility engine (§14).
# Per-request fast gates + offline battery lookup; combined into one credibility state.
# UNKNOWN is never coerced to PASS. Aggregate carries the worst state of its inputs.
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CheckResult:
    id: str
    name: str
    tier: str
    state: str  # PASS | FAIL | UNKNOWN
    detail: str = ""
    threshold: str = ""
    observed: str = ""


@dataclass(frozen=True)
class VerificationResult:
    checks: list[CheckResult]
    aggregate: str
    battery: dict | None = None


# Frozen check register (§14.2).
CHECK_REGISTER = [
    {"id": "V-1", "name": "Model integrity", "tier": "request", "mandatory": True},
    {"id": "V-2", "name": "Steady-state convergence", "tier": "request", "mandatory": True},
    {"id": "V-3", "name": "Unit & range checks", "tier": "request", "mandatory": True},
    {"id": "V-4", "name": "Quadrature consistency", "tier": "request", "mandatory": True},
    {"id": "V-5", "name": "Provenance completeness", "tier": "request", "mandatory": True},
    {"id": "V-6", "name": "Baseline APD90 reproduction", "tier": "battery", "mandatory": True},
    {"id": "V-7", "name": "Baseline qNet reproduction", "tier": "battery", "mandatory": True},
    {"id": "V-8", "name": "Tolerance/timestep sensitivity", "tier": "battery", "mandatory": True},
    {"id": "V-9", "name": "Independent solver cross-check", "tier": "battery", "mandatory": True},
    {"id": "V-10", "name": "Warm-start equivalence", "tier": "battery", "mandatory": True},
    {"id": "V-11", "name": "Known-drug direction", "tier": "battery", "mandatory": True},
    {"id": "V-12", "name": "Prior-art ordering sanity", "tier": "battery", "mandatory": True},
    {"id": "V-13", "name": "K+ directionality", "tier": "battery", "mandatory": True},
    {"id": "V-14", "name": "Stimulus sensitivity", "tier": "battery", "mandatory": False},
    {"id": "V-15", "name": "RA reproducibility", "tier": "battery", "mandatory": False},
    {"id": "V-16", "name": "Negative controls behave", "tier": "battery", "mandatory": True},
]


def aggregate(checks: list[CheckResult]) -> str:
    """§14.3 aggregation truth table."""
    by_id = {c.id: c for c in checks}
    mandatory_fail = [c for c in checks if _mandatory(c.id) and c.state == "FAIL"]
    if mandatory_fail:
        return "FAILED"
    mandatory_unknown = [c for c in checks if _mandatory(c.id) and c.state == "UNKNOWN"]
    if mandatory_unknown:
        return "UNVERIFIED"
    return "VERIFIED"


def _mandatory(check_id: str) -> bool:
    for c in CHECK_REGISTER:
        if c["id"] == check_id:
            return c["mandatory"]
    return True


def run_request_gates(model_ok: bool, converged: bool, ranges_ok: bool, quadrature_ok: bool,
                     provenance_ok: bool) -> VerificationResult:
    """V-1..V-5 (request tier)."""
    checks = [
        CheckResult("V-1", "Model integrity", "request", "PASS" if model_ok else "FAIL",
                    detail="mmt SHA-256 matches CHECKSUMS; labels present"),
        CheckResult("V-2", "Steady-state convergence", "request", "PASS" if converged else "FAIL",
                    detail="C1-C4 satisfied"),
        CheckResult("V-3", "Unit & range checks", "request", "PASS" if ranges_ok else "FAIL",
                    detail="inputs in domain; no NaN/inf; V_peak>0"),
        CheckResult("V-4", "Quadrature consistency", "request", "PASS" if quadrature_ok else "FAIL",
                    detail="trapezoid vs Simpson within 0.1%"),
        CheckResult("V-5", "Provenance completeness", "request", "PASS" if provenance_ok else "FAIL",
                    detail="every used parameter has DOI + VERIFIED"),
    ]
    return VerificationResult(checks=checks, aggregate=aggregate(checks))


def apply_downgrade_tags(aggregate_state: str, tags: list[str]) -> str:
    """§14.3: OUT_OF_CALIBRATED_RANGE / OUT_OF_PHYSIOLOGICAL_RANGE / COMBO_RULE_SENSITIVE /
    partial_panel / RA ARTEFACT_SUSPECTED / BUDGET_EXCEeded cap at UNVERIFIED."""
    if aggregate_state == "FAILED":
        return aggregate_state
    downgrade_tags = {
        "OUT_OF_CALIBRATED_RANGE", "OUT_OF_PHYSIOLOGICAL_RANGE", "COMBO_RULE_SENSITIVE",
        "partial_panel", "ARTEFACT_SUSPECTED", "BUDGET_EXCEEDED",
    }
    if any(t in downgrade_tags for t in tags):
        return "UNVERIFIED"
    return aggregate_state
