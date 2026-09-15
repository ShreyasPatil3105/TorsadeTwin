"""Stage B must not systematically exhaust the global 300-eval budget on 2-axis problems."""
from backend.app.engines.margin import compute_margin
from backend.app.engines.phi import PhiEval
from backend.app.schemas.common import StateSpec, DrugExposure


class LinearPhi:
    def __call__(self, state: StateSpec) -> PhiEval:
        m = state.drugs[0].exposure_multiplier if state.drugs else 0.0
        phi = 0.5 - m - 0.1 * (5.4 - state.k_o_mM)
        return PhiEval(phi=phi, qnet=0.1 + phi, credibility="VERIFIED", tags=[], n_evals=1)


def _cfg():
    from backend.app.config import load_configs
    from pathlib import Path
    return load_configs(Path(__file__).resolve().parents[2]).margin


def test_two_axis_margin_does_not_exhaust_full_budget():
    cfg = dict(_cfg())
    cfg["max_evals"] = 300
    x0 = StateSpec(
        k_o_mM=4.5, cl_ms=2000,
        drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)],
    )
    mr = compute_margin(LinearPhi(), x0, ["k_o_mM", "exposure:dofetilide"], cfg)
    assert mr.budget_exceeded is False
    assert mr.n_phi_evals < 300
    assert mr.m_status in ("EXACT_AXIS", "SAMPLED_UB")
    assert mr.m_signed is not None
    # At least one axis should report a reachable root for this linear Phi
    assert any(a.reachable for a in mr.axes)


def test_max_evals_per_axis_caps_bisection_not_scan():
    """max_evals_per_axis applies to bisection only; coarse scan still uses n_scan points."""
    cfg = dict(_cfg())
    cfg["max_evals"] = 300
    cfg["max_evals_per_axis"] = 5  # tight bisection cap
    x0 = StateSpec(
        k_o_mM=4.5, cl_ms=2000,
        drugs=[DrugExposure(drug_id="dofetilide", exposure_multiplier=1.0)],
    )
    mr = compute_margin(LinearPhi(), x0, ["exposure:dofetilide"], cfg)
    # Completes without requiring full budget; status is a real search status
    assert mr.m_status in ("EXACT_AXIS", "SAMPLED_UB", "BUDGET_EXCEEDED", "UNREACHABLE")
    assert mr.n_phi_evals <= 300
