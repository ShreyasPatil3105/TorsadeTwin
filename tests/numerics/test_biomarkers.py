# L5 biomarker tests (§4.7, §8.1) — analytic surrogate traces with known answers.
from __future__ import annotations

import numpy as np
import pytest

from backend.app.ep.biomarkers import compute_apd90, compute_qnet


def _synthetic_ap(tau: float, v_rest: float = -87.0, v_peak: float = 40.0, t_up: float = 1.0):
    """A synthetic analytic AP with a KNOWN APD90.

    V = v_rest for t < t_up (diastolic), a sharp upstroke to v_peak at t_up, then an
    exponential decay V = v_rest + (v_peak-v_rest)*exp(-(t-t_up)/tau).
    V90 = v_peak - 0.9*(v_peak-v_rest); crossing at t90 = t_up - tau*ln(0.1).
    APD90 = t90 - t_act = -tau*ln(0.1) (t_act = t_up).
    """
    t = np.arange(0.0, 2000.0, 0.1)
    v = np.full_like(t, v_rest)
    i_up = int(round(t_up / 0.1))
    v[i_up] = v_peak
    idx = np.arange(i_up + 1, len(t))
    v[idx] = v_rest + (v_peak - v_rest) * np.exp(-(t[idx] - t_up) / tau)
    return t, v


def test_apd90_analytic_trace():
    tau = 100.0
    t, v = _synthetic_ap(tau)
    apd90, flags = compute_apd90(t, v)
    assert apd90 is not None
    expected = -tau * np.log(0.1)
    assert abs(apd90 - expected) < 1.0


def _full_beat_grid():
    """Uniform 0.1 ms grid over the full periodic beat [0, CL) (20000 points)."""
    return np.arange(20000, dtype=float) * 0.1


def test_qnet_analytic_integral_c_per_f():
    # I_net = 2.0 A/F constant over the full [0, 2000] ms beat -> qNet = 2.0 A/F * 2.0 s = 4.0 C/F.
    t = _full_beat_grid()
    i = np.full_like(t, 2.0)
    trap, simp = compute_qnet(t, i, cl_ms=2000.0)
    assert abs(trap - 4.0) < 1e-6
    # V-4: trapezoid vs Simpson must agree within 0.1%.
    assert abs(trap - simp) / max(abs(trap), 1e-12) < 0.001


def test_qnet_zero_current():
    t = _full_beat_grid()
    i = np.zeros_like(t)
    trap, simp = compute_qnet(t, i, cl_ms=2000.0)
    assert abs(trap) < 1e-12
    assert abs(simp) < 1e-12


def test_qnet_negative_outward_current():
    # Outward-positive convention: a negative (inward) current gives a negative qNet.
    t = _full_beat_grid()
    i = np.full_like(t, -1.0)
    trap, _ = compute_qnet(t, i, cl_ms=2000.0)
    assert trap < 0.0
    assert abs(trap - (-2.0)) < 1e-6


def test_qnet_rejects_incomplete_half_open_grid():
    t = np.arange(0.0, 1999.9, 0.1)
    i = np.ones_like(t)
    with pytest.raises(Exception, match=r"complete half-open \[0, CL\) interval"):
        compute_qnet(t, i, cl_ms=2000.0)


def test_qnet_rejects_odd_interval_count_for_simpson():
    t = np.arange(3, dtype=float) / 3.0
    i = np.ones_like(t)
    with pytest.raises(Exception, match=r"composite Simpson"):
        compute_qnet(t, i, cl_ms=1.0)
