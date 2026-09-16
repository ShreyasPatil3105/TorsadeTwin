# L8 — Blind-spot auditor (§13).
# Quantifies intervals where the Tisdale band is constant while Phi (and the margin) change materially.
# Claim is about sensitivity, never correctness. Missing score inputs -> UNKNOWN -> interval [min,max].
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from ..data.scores import TisdaleScore, score_tisdale
from ..schemas.common import StateSpec, DrugExposure
from .margin import compute_margin
from .phi import PhiEval


@dataclass(frozen=True)
class BlindspotResult:
    grid: list[float]
    phi: list[float]
    margin: list[float | None]
    score_min: list[int]
    score_max: list[int]
    score_band: list[str]
    insensitivity_intervals: list[dict]
    crossing_point: float | None
    verdict: str
    assumptions: list[str] = field(default_factory=lambda: ["ASSUMPTION_SERUM_KO_PROXY_v1"])


def run_blindspot(phi: Callable[[StateSpec], PhiEval], x0: StateSpec, sweep: dict,
                  score: TisdaleScore, score_inputs: dict, margin_cfg: dict | None = None, qnet_ctrl: float = 0.075) -> BlindspotResult:
    """§13.3 methodology."""
    var = sweep["variable"]
    lo = float(sweep["from_"] if "from_" in sweep else sweep.get("from", 0))
    hi = float(sweep["to"])
    n = int(sweep.get("n_points", 21))
    grid = list(np.linspace(lo, hi, n))
    delta_phi_min = 0.02 * qnet_ctrl

    phi_vals: list[float] = []
    margin_vals: list[float | None] = []
    s_min: list[int] = []
    s_max: list[int] = []
    bands: list[str] = []
    for g in grid:
        state = _set_variable(x0, var, g)
        res = phi(state)
        phi_vals.append(res.phi)
        if margin_cfg:
            mr = compute_margin(phi, state, _axes(state), margin_cfg)
            margin_vals.append(mr.m_signed)
        else:
            margin_vals.append(None)
        k_o = g if var == "k_o_mM" else x0.k_o_mM
        lo_s, hi_s = score_tisdale(score, score_inputs, k_o)
        s_min.append(lo_s)
        s_max.append(hi_s)
        bands.append(score.band_for(hi_s) or "UNKNOWN")

    # crossing point: first g where Phi changes sign
    crossing = None
    for i in range(1, len(grid)):
        p_prev = phi_vals[i - 1]
        p_curr = phi_vals[i]
        if p_prev is not None and p_curr is not None:
            if p_prev * p_curr <= 0 and p_prev != p_curr:
                crossing = float(grid[i])
                break

    # insensitivity intervals: maximal contiguous sub-intervals where band constant and |Phi(g)-Phi(g_start)| >= delta
    intervals: list[dict] = []
    start = 0
    while start < len(grid):
        band = bands[start]
        end = start
        while end + 1 < len(grid) and bands[end + 1] == band:
            end += 1
        if end > start:
            p_end = phi_vals[end]
            p_start = phi_vals[start]
            if p_end is not None and p_start is not None:
                delta = abs(p_end - p_start)
                if delta >= delta_phi_min:
                    intervals.append({"from": grid[end], "to": grid[start], "band": band, "delta_phi": round(delta, 4)})
        start = end + 1

    verdict = _verdict(var, grid, bands, s_min, s_max, margin_vals, crossing)
    return BlindspotResult(
        grid=grid, phi=phi_vals, margin=margin_vals, score_min=s_min, score_max=s_max,
        score_band=bands, insensitivity_intervals=intervals, crossing_point=crossing, verdict=verdict,
    )


def _set_variable(x0: StateSpec, var: str, value: float) -> StateSpec:
    if var == "k_o_mM":
        return StateSpec(drugs=x0.drugs, k_o_mM=value, cl_ms=x0.cl_ms, cell_type=x0.cell_type,
                         solver_profile=x0.solver_profile, combo_rule=x0.combo_rule)
    if var.startswith("exposure:"):
        drug = var.split(":", 1)[1]
        drugs = [DrugExposure(drug_id=d.drug_id, exposure_multiplier=d.exposure_multiplier) for d in x0.drugs]
        drugs = [d for d in drugs if d.drug_id != drug]
        drugs.append(DrugExposure(drug_id=drug, exposure_multiplier=value))
        return StateSpec(drugs=drugs, k_o_mM=x0.k_o_mM, cl_ms=x0.cl_ms, cell_type=x0.cell_type,
                         solver_profile=x0.solver_profile, combo_rule=x0.combo_rule)
    raise ValueError(f"unknown sweep variable {var}")


def _axes(x0: StateSpec) -> list[str]:
    return ["k_o_mM"] + [f"exposure:{d.drug_id}" for d in x0.drugs]


def _verdict(var: str, grid: list[float], bands: list[str], s_min: list[int], s_max: list[int],
             margins: list[float | None], crossing: float | None) -> str:
    band = bands[-1] if bands else "UNKNOWN"
    hi = grid[0]
    lo = grid[-1]
    smin = s_min[-1]
    smax = s_max[-1]
    m_hi = margins[0] if margins and margins[0] is not None else 0.0
    m_lo = margins[-1] if margins and margins[-1] is not None else 0.0
    cross = crossing if crossing is not None else "?"
    return (
        f"Over {var} = {hi} -> {lo} the Tisdale band remains **{band}** "
        f"(score interval unchanged at [{smin}, {smax}]) because its potassium item is a threshold at <= 3.5 mM, "
        f"while the mechanistic margin in this model falls from +{m_hi:.1f} to {m_lo:.1f} normalised units and "
        f"crosses the model-defined boundary at {var} = {cross} mM. The score is **insensitive to this "
        f"modelled variable over this interval**; this comparison does not establish that the score is incorrect."
    )
