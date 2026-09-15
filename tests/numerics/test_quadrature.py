# Quadrature consistency (§8.1, V-4): trapezoid vs Simpson within 0.1%.
from __future__ import annotations

import numpy as np

from backend.app.ep.biomarkers import compute_qnet


def test_trapezoid_vs_simpson_within_0_1_percent():
    rng = np.random.default_rng(0)
    t = np.arange(20000, dtype=float) * 0.1
    i = 0.5 + 0.5 * np.sin(2 * np.pi * t / 2000.0) + 0.05 * rng.normal(size=len(t))
    trap, simp = compute_qnet(t, i)
    assert abs(trap - simp) / max(abs(trap), 1e-12) < 0.001


def test_trapezoid_vs_simpson_smooth():
    t = np.arange(20000, dtype=float) * 0.1
    i = np.sin(2 * np.pi * t / 2000.0) + 1.0
    trap, simp = compute_qnet(t, i)
    assert abs(trap - simp) / max(abs(trap), 1e-12) < 0.001
