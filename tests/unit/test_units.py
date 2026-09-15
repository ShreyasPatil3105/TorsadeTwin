from __future__ import annotations

import pytest

from backend.app.services.units import assert_finite, c_per_f_to_uc_per_uf


def test_c_per_f_to_uc_per_uf():
    assert c_per_f_to_uc_per_uf(1.0) == 1.0e6


def test_assert_finite_ok():
    assert_finite(1.0, 2.0, -3.5)


def test_assert_finite_rejects_nan():
    with pytest.raises(ValueError):
        assert_finite(float("nan"))


def test_assert_finite_rejects_inf():
    with pytest.raises(ValueError):
        assert_finite(1.0, float("inf"))
