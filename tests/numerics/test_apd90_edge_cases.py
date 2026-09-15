# APD90 edge cases (§4.7).
from __future__ import annotations

import numpy as np
import pytest

from backend.app.ep.biomarkers import compute_apd90


def _synthetic_ap(tau: float, v_rest: float = -87.0, v_peak: float = 40.0, t_up: float = 1.0):
    t = np.arange(0.0, 2000.0, 0.1)
    v = np.full_like(t, v_rest)
    i_up = int(round(t_up / 0.1))
    v[i_up] = v_peak
    idx = np.arange(i_up + 1, len(t))
    v[idx] = v_rest + (v_peak - v_rest) * np.exp(-(t[idx] - t_up) / tau)
    return t, v


def test_apd90_linear_interpolation():
    # V90 is crossed between two samples -> linear interpolation refinement.
    tau = 100.0
    t, v = _synthetic_ap(tau)
    apd90, flags = compute_apd90(t, v)
    assert apd90 is not None
    # exact APD90 of the analytic trace = -tau*ln(0.1); interpolation must be within 1 ms
    assert abs(apd90 - (-tau * np.log(0.1))) < 1.0


def test_apd90_extreme_flag():
    tau = 500.0
    t, v = _synthetic_ap(tau)
    apd90, flags = compute_apd90(t, v)
    assert apd90 is not None and apd90 > 800.0
    assert "APD90_EXTREME" in flags


def test_apd90_no_upstroke_raises():
    t = np.arange(0.0, 2000.0, 0.1)
    v = np.full_like(t, -80.0)  # no upstroke
    with pytest.raises(Exception):
        compute_apd90(t, v)


def test_apd90_repol_failure_no_crossing():
    # V stays above V90 for the whole cycle -> no downward crossing -> REPOL_FAILURE
    v_rest = -10.0
    v_peak = 40.0
    t = np.arange(0.0, 2000.0, 0.1)
    v = np.full_like(t, v_peak)  # flat at peak, never repolarizes below V90
    v[-1] = v_rest
    apd90, flags = compute_apd90(t, v)
    assert apd90 is None
    assert "REPOL_FAILURE" in flags
