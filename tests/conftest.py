# Test helpers: analytic surrogate Phi evaluators + shared fixtures (§26.3 rule 1).
from __future__ import annotations

import math

import numpy as np

from backend.app.engines.phi import PhiEval
from backend.app.schemas.common import DrugExposure, StateSpec


def analytic_phi_plane(intercept: float = 1.0, k_slope: float = 1.0, m_slope: float = 1.0):
    """Phi = intercept + k_slope*(k_o - k0) + m_slope*(log2(m+eps) - log2(m0+eps)).

    A plane in (k_o, log2-exposure) space with a known closed-form distance.
    """

    def _eval(state: StateSpec) -> PhiEval:
        k0 = 4.0
        m0 = 1.0
        k = state.k_o_mM
        m = state.drugs[0].exposure_multiplier if state.drugs else 1.0
        u_m = math.log2(m + 1e-6)
        u_m0 = math.log2(m0 + 1e-6)
        phi = intercept + k_slope * (k - k0) + m_slope * (u_m - u_m0)
        return PhiEval(phi=phi, qnet=phi + 0.075, credibility="VERIFIED", n_evals=1)

    return _eval


def analytic_phi_paraboloid(center_k: float = 3.5, center_m: float = 2.0, radius: float = 0.5):
    """Phi = (k_o - center_k)^2 + (log2(m) - log2(center_m))^2 - radius^2.

    A paraboloid (circle in normalised space) with a known closed-form distance.
    """

    def _eval(state: StateSpec) -> PhiEval:
        k = state.k_o_mM
        m = state.drugs[0].exposure_multiplier if state.drugs else 1.0
        u_m = math.log2(m + 1e-6)
        u_mc = math.log2(center_m + 1e-6)
        phi = (k - center_k) ** 2 + (u_m - u_mc) ** 2 - radius**2
        return PhiEval(phi=phi, qnet=phi + 0.075, credibility="VERIFIED", n_evals=1)

    return _eval


def analytic_phi_nonmonotone():
    """Phi with two roots along the k axis (non-monotone)."""

    def _eval(state: StateSpec) -> PhiEval:
        k = state.k_o_mM
        phi = (k - 3.0) * (k - 4.5)
        return PhiEval(phi=phi, qnet=phi + 0.075, credibility="VERIFIED", n_evals=1)

    return _eval


def make_state(k_o_mM: float = 4.0, m: float = 1.0, drug_id: str = "dofetilide", cl_ms: int = 2000) -> StateSpec:
    return StateSpec(drugs=[DrugExposure(drug_id=drug_id, exposure_multiplier=m)], k_o_mM=k_o_mM, cl_ms=cl_ms)


def margin_cfg() -> dict:
    return {
        "scales": {"k_o_mM": 1.0, "exposure": 1.0},
        "eps_log2": 1e-6,
        "weights": {"default": 1.0},
        "box": {"k_o_mM": [3.0, 5.5], "exposure_multiplier": [0.0625, 4.0]},
        "tol_z": 1e-3,
        "max_iter_bisect": 20,
        "max_evals_per_axis": 30,
        "tol_phi": 1e-4,
        "n_scan_coarse": 9,
        "n_scan_fine": 25,
        "max_evals": 300,
        "directions": {"n_angles_2d": 64, "n_fib_3d": 128, "n_halton_max": 256, "halton_seed": 12345,
                        "radial_step": 0.25, "max_iter_bisect_stage_b": 15},
        "stage_c": {"maxiter": 30, "fd_step": 1e-3},
    }
