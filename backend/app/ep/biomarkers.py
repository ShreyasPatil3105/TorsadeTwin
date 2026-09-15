# L5 — biomarker engine (§4.7, §4.9, §8.1, §8.6).
# qNet (primary), APD90 (secondary), RA flag (tertiary, never definitional).
from __future__ import annotations

import numpy as np

from ..services.errors import TorsadeTwinError


QNET_CURRENTS = ["INaL", "ICaL", "IKr", "IKs", "IK1", "Ito"]


def compute_apd90(t_ms: np.ndarray, v_mV: np.ndarray) -> tuple[float | None, list[str]]:
    """APD90 per §4.7. Returns (apd90_ms, ra_flags)."""
    flags: list[str] = []
    if len(t_ms) < 3:
        return None, ["REPOL_FAILURE"]
    dt = t_ms[1] - t_ms[0]
    dV = np.gradient(v_mV, dt)
    t_act = float(t_ms[int(np.argmax(dV))])
    idx_act = int(np.argmax(dV))
    seg = v_mV[idx_act:]
    v_peak = float(np.max(seg))
    if v_peak < 0.0:
        raise TorsadeTwinError("E_NO_UPSTROKE", "No upstroke detected (V_peak < 0 mV).", http_status=422)
    v_rest = float(v_mV[-1])
    v_90 = v_peak - 0.90 * (v_peak - v_rest)
    t_peak = float(t_ms[idx_act + int(np.argmax(seg))])
    # first downward crossing of V_90 after t_peak, linear interpolation
    t90: float | None = None
    crossings = 0
    for i in range(idx_act + 1, len(t_ms) - 1):
        if v_mV[i - 1] >= v_90 >= v_mV[i]:
            frac = (v_mV[i - 1] - v_90) / (v_mV[i - 1] - v_mV[i]) if v_mV[i - 1] != v_mV[i] else 0.5
            t_cross = t_ms[i - 1] + frac * (t_ms[i] - t_ms[i - 1])
            crossings += 1
            if t90 is None and t_cross > t_peak:
                t90 = t_cross
    if t90 is None:
        flags.append("REPOL_FAILURE")
        return None, flags
    if crossings > 1:
        flags.append("MULTI_CROSSING")
    apd90 = t90 - t_act
    if apd90 > 800.0:
        flags.append("APD90_EXTREME")
    return apd90, flags


def compute_qnet(t_ms: np.ndarray, i_net_A_per_F: np.ndarray, cl_ms: float | None = None) -> tuple[float, float]:
    """qNet over one complete analysis beat sampled on ``[0, CL]`` (§8.1).

    I_net is in A/F and t is in ms; converting ms -> s gives C/F (factor 1e-3).
    The primary trapezoid and Simpson cross-check use the same complete grid. No
    samples are silently discarded.
    """
    t = np.asarray(t_ms, dtype=float)
    y = np.asarray(i_net_A_per_F, dtype=float)
    if t.ndim != 1 or y.ndim != 1 or len(t) != len(y) or len(t) < 3:
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "Invalid qNet analysis grid.",
            detail="Time and current arrays must be one-dimensional, equal length, and contain at least three samples.",
            http_status=422,
        )
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)):
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "Non-finite qNet analysis data.",
            http_status=422,
        )
    if not np.isclose(t[0], 0.0, rtol=0.0, atol=1e-9):
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "qNet grid must start at t=0 ms.",
            detail=f"t[0]={t[0]}",
            http_status=422,
        )
    h = float(t[1] - t[0])
    if cl_ms is None:
        cl_ms = float(t[-1] + h)
    cl_ms = float(cl_ms)
    if cl_ms <= 0:
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "qNet CL must be positive.",
            detail=f"CL={cl_ms}",
            http_status=422,
        )
    dt = np.diff(t)
    if h <= 0 or not np.allclose(dt, h, rtol=0.0, atol=1e-9):
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "qNet grid must be uniform.",
            detail=f"first step={h} ms",
            http_status=422,
        )
    if np.isclose(t[-1], cl_ms, rtol=0.0, atol=1e-9):
        if (len(t) - 1) % 2 != 0:
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "qNet grid is incompatible with composite Simpson cross-check.",
                detail=f"{len(t) - 1} intervals; an even count is required.",
                http_status=422,
            )
        trap = float(np.trapezoid(y, t)) * 1e-3
        simp = h / 3.0 * (y[0] + y[-1] + 4.0 * np.sum(y[1:-1:2]) + 2.0 * np.sum(y[2:-1:2]))
        return trap, float(simp) * 1e-3

    # Myokit excludes a requested log time equal to Simulation.run()'s end. At
    # convergence the final endpoint is therefore the periodic start value; use
    # that endpoint explicitly for both required quadratures rather than a
    # rectangular sum over a shortened beat.
    if not np.isclose(t[-1] + h, cl_ms, rtol=0.0, atol=1e-9):
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "qNet grid must span the complete half-open [0, CL) interval.",
            detail=f"expected final sample {cl_ms} ms or periodic sample {cl_ms - h} ms, got {t[-1]} ms",
            http_status=422,
        )
    if len(t) % 2 != 0:
        raise TorsadeTwinError(
            "E_NUMERICAL_INSTABILITY",
            "qNet grid is incompatible with composite Simpson cross-check.",
            detail=f"{len(t)} half-open samples gives an odd interval count; an even count is required.",
            http_status=422,
        )
    closed_t = np.append(t, cl_ms)
    closed_y = np.append(y, y[0])
    trap = float(np.trapezoid(closed_y, closed_t)) * 1e-3
    simp = h / 3.0 * (closed_y[0] + closed_y[-1] + 4.0 * np.sum(closed_y[1:-1:2]) + 2.0 * np.sum(closed_y[2:-1:2]))
    return trap, float(simp) * 1e-3


def compute_ra_flags(t_ms: np.ndarray, v_mV: np.ndarray, apd90: float | None) -> list[str]:
    """RA annotation per §8.6 (secondary only; never enters Phi/margin)."""
    flags: list[str] = []
    if apd90 is None:
        flags.append("REPOL_FAILURE")
    dt = t_ms[1] - t_ms[0]
    dV = np.gradient(v_mV, dt)
    v_peak = float(np.max(v_mV))
    v_rest = float(v_mV[-1])
    threshold = v_peak - 0.3 * (v_peak - v_rest)
    # EAD_CANDIDATE: dV/dt > +0.01 mV/ms sustained >= 5 ms while V < 0 and below threshold
    below = v_mV < 0.0
    after_fall = v_mV < threshold
    pos = dV > 0.01
    active = below & after_fall & pos
    run = 0
    for a in active:
        if a:
            run += 1
            if run * dt >= 5.0:
                flags.append("EAD_CANDIDATE")
                break
        else:
            run = 0
    if v_mV[-1] > -40.0:
        flags.append("REPOL_FAILURE")
    return flags


def compute_diagnostics(t_ms: np.ndarray, v_mV: np.ndarray) -> dict:
    dt = t_ms[1] - t_ms[0]
    dV = np.gradient(v_mV, dt)
    return {
        "v_rest_mV": float(v_mV[-1]),
        "v_peak_mV": float(np.max(v_mV)),
        "dvdt_max_mV_per_ms": float(np.max(dV)),
    }
