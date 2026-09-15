from __future__ import annotations

import inspect

import numpy as np
import pytest

from backend.app.ep.simulate import EpEngine


class _FakeSim:
    def __init__(self):
        self.requested = []
        self._time = 0.0

    def time(self):
        return self._time

    def run(self, duration, *, log_times, log):
        requested = np.asarray(log_times, dtype=float)
        self.requested.append(requested)
        end = self._time + duration
        emitted = requested[(requested >= self._time) & (requested < end)]
        self._time = end
        return {name: np.zeros(len(emitted)) for name in log}


def test_run_beat_requests_exact_half_open_grid():
    engine = EpEngine.__new__(EpEngine)
    sim = _FakeSim()
    log = engine._run_beat(sim, 2000.0, 0.1)
    requested = sim.requested[0]
    assert requested[0] == 0.0
    assert requested[-1] == 1999.9
    assert len(requested) == 20000
    assert np.allclose(np.diff(requested), 0.1, rtol=0.0, atol=1e-12)
    assert len(log["membrane.v"]) == 20000


def test_consecutive_run_beat_grids_follow_simulation_time():
    engine = EpEngine.__new__(EpEngine)
    sim = _FakeSim()
    first = engine._run_beat(sim, 2000.0, 0.1)
    second = engine._run_beat(sim, 2000.0, 0.1)
    assert len(first["membrane.v"]) == 20000
    assert len(second["membrane.v"]) == 20000
    assert sim.requested[1][0] == 2000.0
    assert sim.requested[1][-1] == 3999.9


class _BadLogSim(_FakeSim):
    def run(self, duration, *, log_times, log):
        requested = np.asarray(log_times, dtype=float)
        self.requested.append(requested)
        self._time += duration
        return {name: np.zeros(len(requested) - 1) for name in log}


def test_run_beat_rejects_incomplete_grid():
    engine = EpEngine.__new__(EpEngine)
    with pytest.raises(Exception, match="unexpected sample count"):
        engine._run_beat(_BadLogSim(), 2000.0, 0.1)


def test_simulation_uses_myokit_1392_max_step_api():
    source = inspect.getsource(EpEngine.simulate)
    assert 'sim.set_max_step_size(self.solver_profile["max_step_ms"])' in source
    assert 'sim.set_max_step(self.solver_profile["max_step_ms"])' not in source


class _ToleranceSim:
    def __init__(self):
        self.calls = []

    def set_tolerance(self, *args):
        self.calls.append(args)


def test_simulation_uses_myokit_tolerance_argument_order():
    import inspect
    source = inspect.getsource(EpEngine.simulate)
    assert 'sim.set_tolerance(self.solver_profile["atol"], self.solver_profile["rtol"])' in source



class _LiteralRhs:
    def __init__(self, value):
        self._value = value

    def eval(self):
        return self._value


class _LiteralVariable:
    def __init__(self, value):
        self._rhs = _LiteralRhs(value)

    def is_literal(self):
        return True

    def rhs(self):
        return self._rhs


class _ScaleModel:
    def __init__(self, value):
        self.variable = _LiteralVariable(value)

    def get(self, name):
        assert name == "IKr.GKr_b"
        return self.variable


class _ScaleSim:
    def __init__(self):
        self.constants = {}

    def set_constant(self, name, value):
        self.constants[name] = value


def test_unblocked_fraction_scales_vendored_conductance():
    engine = EpEngine.__new__(EpEngine)
    model = _ScaleModel(0.04658545454545456)
    sim = _ScaleSim()
    engine._set_channel_scale(sim, model, "IKr", 1.0)
    assert sim.constants["IKr.GKr_b"] == 0.04658545454545456
    engine._set_channel_scale(sim, model, "IKr", 0.5)
    assert sim.constants["IKr.GKr_b"] == 0.5 * 0.04658545454545456
