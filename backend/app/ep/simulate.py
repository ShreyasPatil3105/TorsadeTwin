# L4 — steady-state simulation engine (§4).
# Deterministic pacing to steady state (C1-C4), final-beat extraction, warm starts.
# Fails safely (E_NO_STEADY_STATE / E_SOLVER / E_NUMERICAL_INSTABILITY) per §4.4.
from __future__ import annotations

from dataclasses import dataclass, field

import os
import numpy as np

from ..services.errors import TorsadeTwinError
from .biomarkers import QNET_CURRENTS, compute_apd90, compute_qnet, compute_ra_flags, compute_diagnostics


def _ensure_sundials_includes(myokit_module=None) -> None:
    """Ensure Debian/Kali OpenMPI include paths are known to Myokit/Sundials."""
    mpi_dirs = [
        "/usr/lib/x86_64-linux-gnu/openmpi/include",
        "/usr/include/x86_64-linux-gnu/mpi",
        "/usr/include/x86_64-linux-gnu/openmpi",
        "/usr/include/openmpi-x86_64",
        "/usr/include/mpich",
        "/usr/include/x86_64-linux-gnu/mpich",
    ]
    if myokit_module is not None and hasattr(myokit_module, "SUNDIALS_INC") and isinstance(myokit_module.SUNDIALS_INC, list):
        for d in mpi_dirs:
            if os.path.isdir(d) and d not in myokit_module.SUNDIALS_INC:
                myokit_module.SUNDIALS_INC.append(d)
    for d in mpi_dirs:
        if os.path.isdir(d):
            cpath = os.environ.get("C_INCLUDE_PATH", "")
            if d not in cpath:
                os.environ["C_INCLUDE_PATH"] = f"{d}:{cpath}" if cpath else d
            cp = os.environ.get("CPATH", "")
            if d not in cp:
                os.environ["CPATH"] = f"{d}:{cp}" if cp else d



@dataclass
class SimulationResult:
    converged: bool
    beats_run: int
    qnet_C_per_F: float | None = None
    qnet_simpson_C_per_F: float | None = None
    apd90_ms: float | None = None
    v_rest_mV: float | None = None
    v_peak_mV: float | None = None
    dvdt_max_mV_per_ms: float | None = None
    ra_flags: list[str] = field(default_factory=list)
    trace_t_ms: list[float] = field(default_factory=list)
    trace_v_mV: list[float] = field(default_factory=list)
    trace_i_net_A_per_F: list[float] = field(default_factory=list)
    convergence: dict = field(default_factory=dict)
    state_vector: list[float] | None = None
    diagnostics: dict = field(default_factory=dict)


class EpEngine:
    """Runs the vendored ORd-CiPA v1.0 model to steady state under a declared state.

    The Myokit runtime and the .mmt artefact are required. When either is unavailable the
    engine raises the specified error codes (E_MODEL_UNAVAILABLE) so callers fail safely.
    """

    def __init__(self, model_info, solver_profile: dict, protocol: dict, state_scales: dict):
        self.model_info = model_info
        self.solver_profile = solver_profile
        self.protocol = protocol
        self.state_scales = state_scales
        self._voltage_label = model_info.labels["membrane_potential"]
        self._current_labels = dict(model_info.qnet_current_labels)

    def simulate(self, state, block_unblocked: dict[str, float], return_trace: bool = False,
                 warm_state: list[float] | None = None) -> SimulationResult:
        try:
            import myokit  # type: ignore

            _ensure_sundials_includes(myokit)
        except ImportError as exc:
            raise TorsadeTwinError(
                "E_MODEL_UNAVAILABLE", "Myokit is not installed; the EP engine cannot run.",
                detail="Install backend/requirements.txt (requires network once).",
                remediation="pip install -r backend/requirements.txt", http_status=503,
            ) from exc
        # Cache loaded model on the engine instance (no scientific change;
        # avoids repeated disk parse on every Phi evaluation).
        if getattr(self, "_cached_model", None) is None:
            self._cached_model = myokit.load_model(self.model_info.artefact)
        model = self._cached_model

        cl = float(state.cl_ms)
        offset = float(self.protocol["stimulus"]["offset_ms"])
        stim_dur = float(self.protocol["stimulus"]["duration_ms"])
        stim_amp = float(self.protocol["stimulus"]["amplitude_A_per_F"])
        dt_log = float(self.solver_profile.get("dt_log_ms", 0.1))
        n_pre = int(self.protocol.get("n_prepace", 1000))
        n_extra_max = int(self.protocol.get("n_extra_max", 1000))
        n_extra_block = int(self.protocol.get("n_extra_block", 100))
        # SPEC warm start: initialise from neighbour state, then run n_warm beats
        # and require C1–C4. Does not alter cold-start n_prepace=1000.
        if warm_state is not None:
            n_pre = int(self.protocol.get("n_warm", 200))
            n_extra_max = max(n_extra_max, n_pre)  # allow extension if needed

        # Keep the vendored model's own time-dependent stimulus expression.
        # We only restart the solver at bounded block boundaries. This avoids
        # the two failure modes caused by the previous external-pacing adapter:
        # (1) protocol/reset phase ambiguity and (2) million-ms absolute solver
        # clocks. The physiological state is preserved across each restart.
        state_names = [str(s) for s in model.states()]
        try:
            nai_index = state_names.index("intracellular_ions.nai")
            d_index = state_names.index("IKr.D")
        except ValueError as exc:
            raise TorsadeTwinError(
                "E_MODEL_BINDING",
                "Required model state is missing.",
                detail=str(exc), http_status=503,
            ) from exc
        eps_map = self.state_scales.get("state_scales", {}) if isinstance(self.state_scales, dict) else {}

        # Force D initial value on the model object before first compilation so that
        # log(IKr.D) expressions are well-defined in the generated C code.
        try:
            model.get("IKr.D").set_initial_value(1.0)
        except Exception:
            pass

        def make_sim(restored_state: list[float] | None):
            # Reuse compiled Simulation across calls on this engine (reset+set_state
            # each time). First call still compiles once.
            if getattr(self, "_compiled_sim", None) is None:
                try:
                    sim = myokit.Simulation(model)
                except Exception as exc:
                    raise TorsadeTwinError(
                        "E_SOLVER",
                        "Myokit ODE simulation engine failed to compile.",
                        detail=str(exc),
                        remediation="On Windows: Install Microsoft C++ Build Tools (https://visualstudio.microsoft.com/visual-cpp-build-tools/). On Linux/Ubuntu: run 'sudo apt install build-essential libsundials-dev'.",
                        http_status=500,
                    ) from exc
                sim.set_tolerance(self.solver_profile["atol"], self.solver_profile["rtol"])
                sim.set_max_step_size(self.solver_profile["max_step_ms"])
                sim.set_constant("extracellular.ko", state.k_o_mM)
                for channel, f in block_unblocked.items():
                    self._set_channel_scale(sim, model, channel, f)
                for name in ["drug", "herg.drug", "binding.drug", "drug_conc"]:
                    if name in model:
                        sim.set_constant(name, 0.0)
                        break
                # These are literal model stimulus constants; the vendored piecewise
                # Istim equation remains authoritative and is periodic in model time.
                sim.set_constant("membrane.i_Stim_Start", offset)
                sim.set_constant("membrane.i_Stim_End", 1e17)
                sim.set_constant("membrane.i_Stim_Period", cl)
                sim.set_constant("membrane.i_Stim_PulseDuration", stim_dur)
                sim.set_constant("membrane.i_Stim_Amplitude", stim_amp)
                self._compiled_sim = sim
            else:
                sim = self._compiled_sim
            # Always refresh Ko and channel scales (drug block differs per Phi call).
            sim.set_constant("extracellular.ko", state.k_o_mM)
            # Reset all known channels to unblocked, then apply current block map.
            for channel in ("IKr", "ICaL", "INa_peak", "INaL", "IKs", "IK1", "Ito"):
                self._set_channel_scale(sim, model, channel, float(block_unblocked.get(channel, 1.0)))
            # Reinitialize CVODES at local t=0 while preserving (or setting) physiology.
            sim.reset()
            if restored_state is None:
                initial = list(sim.state())
                initial[d_index] = 1.0
                sim.set_state(initial)
            else:
                restored = list(restored_state)
                restored[d_index] = 1.0
                sim.set_state(restored)
            return sim

        sim = make_sim(warm_state)

        def run_block(simulation, n_beats: int, capture_last_two: bool):
            n_beats = int(n_beats)
            if n_beats < 1:
                raise TorsadeTwinError("E_NUMERICAL_INSTABILITY", "Invalid pacing block.",
                                        detail=f"n_beats={n_beats}", http_status=422)
            if capture_last_two and n_beats < 2:
                raise TorsadeTwinError("E_NUMERICAL_INSTABILITY", "At least two beats are required to capture convergence state.",
                                        detail=f"n_beats={n_beats}", http_status=422)
            try:
                if capture_last_two:
                    discard = n_beats - 2
                    if discard:
                        simulation.run(float(discard * cl), log=myokit.LOG_NONE)
                    prev = self._run_contiguous_beat(simulation, cl, dt_log)
                    prev_state = list(simulation.state())
                    cur = self._run_contiguous_beat(simulation, cl, dt_log)
                    cur_state = list(simulation.state())
                    return (self._beat_from_log(prev, prev_state, nai_index, cl),
                            self._beat_from_log(cur, cur_state, nai_index, cl), cur_state)
                simulation.run(float(n_beats * cl), log=myokit.LOG_NONE)
                return None, None, list(simulation.state())
            except Exception as exc:
                if isinstance(exc, TorsadeTwinError):
                    raise
                raise TorsadeTwinError(
                    "E_SOLVER",
                    "ODE simulation execution error.",
                    detail=str(exc),
                    http_status=500,
                ) from exc

        # Continuous pacing within one Simulation: do not reset/recreate CVODES
        # between blocks. Resets discard step-size history and add pure overhead
        # (~same scientific trajectory, higher wall-clock). Bounded absolute time
        # for n_prepace=1000 * CL=2000 ms remains well within CVODES range.
        beats_done = 0
        remaining = n_pre
        conv = None
        prev = cur = None
        cur_state = list(sim.state())
        while remaining > 0:
            block_n = min(n_extra_block, remaining)
            if block_n == remaining and block_n >= 2:
                prev, cur, cur_state = run_block(sim, block_n, True)
            else:
                _, _, cur_state = run_block(sim, block_n, False)
            beats_done += block_n
            remaining -= block_n
            # Intentionally NO make_sim here — keep continuous integration.
        if prev is None or cur is None:
            raise TorsadeTwinError("E_NUMERICAL_INSTABILITY", "Unable to capture final pre-pacing beats.", http_status=503)
        conv = self._convergence(prev, cur, state_names, eps_map)

        if conv["converged"]:
            # Analysis beat continues in the same solver instance (contiguous).
            return self._analysis_beat_from_contiguous(sim, cl, dt_log, beats_done, return_trace, conv, nai_index)

        while beats_done < n_pre + n_extra_max:
            block_n = min(n_extra_block, n_pre + n_extra_max - beats_done)
            if block_n < 2:
                raise TorsadeTwinError("E_NUMERICAL_INSTABILITY", "Convergence block must contain at least two beats.", http_status=422)
            prev, cur, cur_state = run_block(sim, block_n, True)
            beats_done += block_n
            conv = self._convergence(prev, cur, state_names, eps_map)
            if conv["converged"]:
                return self._analysis_beat_from_contiguous(sim, cl, dt_log, beats_done, return_trace, conv, nai_index)

        raise TorsadeTwinError("E_NO_STEADY_STATE", "Steady-state convergence was not reached within the configured beat budget.",
                               detail=f"beats_run={beats_done}", http_status=422)

    def _run_contiguous_beat(self, sim, cl: float, dt_log: float):
        """Run one logged beat without rewinding Simulation time.

        Used only inside a bounded solver block. The protocol remains in native
        Myokit time, so its scheduled stimulus events are preserved exactly.
        """
        if cl <= 0 or dt_log <= 0:
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY", "Invalid analysis grid parameters.",
                detail=f"CL={cl}, dt_log={dt_log}", http_status=422,
            )
        n_steps = int(round(cl / dt_log))
        if n_steps < 2 or not np.isclose(n_steps * dt_log, cl, rtol=0.0, atol=1e-9):
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "CL is not representable on the declared uniform logging grid.",
                detail=f"CL={cl}, dt_log={dt_log}", http_status=422,
            )
        start = float(sim.time())
        log_times = start + np.arange(n_steps, dtype=float) * dt_log
        voltage_label = getattr(self, "_voltage_label", "membrane.v")
        current_labels = getattr(self, "_current_labels", {c: f"{c}.{c}" for c in QNET_CURRENTS})
        try:
            log = sim.run(
                float(cl),
                log_times=log_times,
                log=[voltage_label, *current_labels.values()],
            )
        except TypeError as exc:
            raise TorsadeTwinError(
                "E_SOLVER",
                "Myokit did not accept the explicit analysis-beat time grid.",
                detail=str(exc),
                remediation="Use a Myokit version supporting Simulation.run(log_times=...).",
                http_status=503,
            ) from exc
        actual = len(log[voltage_label])
        if actual != n_steps:
            raise TorsadeTwinError(
                "E_SOLVER",
                "Analysis-beat log has an unexpected sample count.",
                detail=f"expected {n_steps} samples; got {actual}", http_status=503,
            )
        return log

    def _analysis_beat_from_contiguous(self, sim, cl, dt_log, beats_done, return_trace, conv, nai_index):
        """Run the single post-convergence analysis beat in the current solver block."""
        log = self._run_contiguous_beat(sim, cl, dt_log)
        state = list(sim.state())
        beat = self._beat_from_log(log, state, nai_index, cl)
        t_rel = beat["t"] - beat["t"][0]
        ra = compute_ra_flags(t_rel, beat["v"], beat["apd90_ms"])
        result = SimulationResult(
            converged=True,
            beats_run=beats_done + 1,
            qnet_C_per_F=beat["qnet_C_per_F"],
            qnet_simpson_C_per_F=beat["qnet_simpson_C_per_F"],
            apd90_ms=beat["apd90_ms"],
            v_rest_mV=beat["v_rest_mV"],
            v_peak_mV=beat["v_peak_mV"],
            dvdt_max_mV_per_ms=beat["dvdt_max_mV_per_ms"],
            ra_flags=ra,
            convergence=conv,
            state_vector=state,
            diagnostics={
                "v_rest_mV": beat["v_rest_mV"],
                "v_peak_mV": beat["v_peak_mV"],
                "dvdt_max_mV_per_ms": beat["dvdt_max_mV_per_ms"],
            },
        )
        if return_trace:
            result.trace_t_ms = list(t_rel)
            result.trace_v_mV = list(beat["v"])
            result.trace_i_net_A_per_F = list(beat["i_net"])
        return result

    # ---------- helpers ----------

    def _capture_last_two(self, sim, cl, offset, dt_log, n_beats, beats_done, nai_index):
        """Pace ``n_beats`` cycles while keeping Myokit time local to one cycle.

        The ORd-CiPA stimulus is periodic in ``environment.time``. Carrying a
        Myokit clock into the millions of milliseconds is numerically unsafe: at
        large absolute times CVODES loses floating-point resolution and can get
        trapped taking zero-length steps. The cell state, not the absolute clock,
        carries the physiological history, so each completed cycle is re-zeroed
        to time 0 while preserving the state vector. This keeps the stimulus phase
        identical on every cycle and prevents catastrophic absolute-time loss of
        precision.
        """
        n_beats = int(n_beats)
        if n_beats < 2:
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "At least two beats are required to capture convergence state.",
                detail=f"n_beats={n_beats}",
                http_status=422,
            )
        # IMPORTANT: Simulation.set_time(0) is not sufficient to reinitialize
        # CVODES after it has already integrated forward. Myokit can retain the
        # integrator's internal time even when the public clock is rewound.
        # Reinitialize the simulation at each cycle while restoring the evolved
        # state. This preserves physiological history but gives CVODES a fresh
        # local clock [0, CL] on every beat. Constants/protocol configuration are
        # retained by Simulation.reset().
        for _ in range(n_beats - 2):
            self._pace_beat(sim, cl)
        log_prev = self._run_beat(sim, cl, dt_log)
        state_prev = list(sim.state())
        log_cur = self._run_beat(sim, cl, dt_log)
        state_cur = list(sim.state())
        return (self._beat_from_log(log_prev, state_prev, nai_index, cl),
                self._beat_from_log(log_cur, state_cur, nai_index, cl))

    def _pace_beat(self, sim, cl: float):
        """Advance one physiological cycle with a freshly initialized CVODES clock.

        ``Simulation.set_time(0)`` only rewinds the exposed simulation time; it
        does not reliably reinitialize the CVODES integrator after long runs.
        Saving the evolved state, calling ``reset()``, and restoring that state
        creates a genuinely fresh integrator at t=0 without resetting physiology.
        The protocol constants remain configured across ``reset()``.
        """
        if cl <= 0:
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "Invalid cycle length.",
                detail=f"CL={cl}",
                http_status=422,
            )
        state = list(sim.state())
        sim.reset()
        sim.set_state(state)
        try:
            import myokit  # type: ignore
            sim.run(float(cl), log=myokit.LOG_NONE)
        except Exception as exc:
            # Preserve the underlying Myokit exception for the caller while
            # ensuring this helper never attempts tiny epsilon-duration runs.
            raise
        # Leave the evolved state in place but restart the public/integrator
        # clock for the next beat. reset()+set_state() is intentionally used
        # rather than set_time(0) for the same reason as above.
        state = list(sim.state())
        sim.reset()
        sim.set_state(state)

    def _run_beat(self, sim, cl: float, dt_log: float):
        """Run one beat on the exact half-open analysis grid [0, CL).

        Simulation time is deliberately local to the current cycle. The evolved
        physiological state persists between calls, while resetting time prevents
        CVODES from losing floating-point resolution after hundreds of thousands of
        milliseconds of cumulative pacing.
        """
        if cl <= 0 or dt_log <= 0:
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "Invalid analysis grid parameters.",
                detail=f"CL={cl}, dt_log={dt_log}",
                http_status=422,
            )
        n_steps = int(round(cl / dt_log))
        if n_steps < 2 or not np.isclose(n_steps * dt_log, cl, rtol=0.0, atol=1e-9):
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "CL is not representable on the declared uniform logging grid.",
                detail=f"CL={cl}, dt_log={dt_log}",
                http_status=422,
            )
        log_times = np.arange(n_steps, dtype=float) * dt_log
        voltage_label = getattr(self, "_voltage_label", "membrane.v")
        current_labels = getattr(self, "_current_labels", {c: f"{c}.{c}" for c in QNET_CURRENTS})
        is_myokit = sim.__class__.__module__.startswith("myokit")
        try:
            if is_myokit:
                import myokit  # type: ignore
                sim.set_time(0.0)
                # Integrate the complete physiological cycle on a fresh local
                # CVODES clock. The analysis grid itself is half-open [0, CL),
                # so the endpoint is not included in log_times; no epsilon run
                # or floating-point boundary hack is needed.
                log = sim.run(
                    float(cl),
                    log_times=log_times,
                    log=[voltage_label, *current_labels.values()],
                )
            else:
                # Lightweight test doubles retain their historical cumulative
                # clock contract; production Myokit uses local cycle time.
                start = float(sim.time())
                absolute_times = start + log_times
                log = sim.run(
                    float(cl),
                    log_times=absolute_times,
                    log=[voltage_label, *current_labels.values()],
                )
        except TypeError as exc:
            raise TorsadeTwinError(
                "E_SOLVER",
                "Myokit did not accept the explicit analysis-beat time grid.",
                detail=str(exc),
                remediation="Use a Myokit version supporting Simulation.run(log_times=...).",
                http_status=503,
            ) from exc
        expected = n_steps
        actual = len(log[voltage_label])
        if actual != expected:
            raise TorsadeTwinError(
                "E_SOLVER",
                "Analysis-beat log has an unexpected sample count.",
                detail=f"expected {expected} samples from Myokit for CL={cl} ms; got {actual}",
                http_status=503,
            )
        # Reinitialize CVODES at t=0 while preserving the just-evolved state.
        # This is required because rewinding only the exposed time can leave the
        # internal CVODES clock at the previous absolute time.
        if is_myokit:
            state = list(sim.state())
            sim.reset()
            sim.set_state(state)
        return log

    def _beat_from_log(self, log, state, nai_index, cl_ms=None):
        # _run_beat() supplies an explicit uniform time grid. Myokit 1.39.2
        # does not attach a log.time() key for explicit log_times, so reconstruct
        # the declared grid here as well.
        if cl_ms is None:
            raise TorsadeTwinError(
                "E_NUMERICAL_INSTABILITY",
                "CL is required to reconstruct the analysis-beat time grid.",
                http_status=422,
            )

        cl_ms = float(cl_ms)
        dt_log = float(self.solver_profile.get("dt_log_ms", 0.1))
        n_steps = int(round(cl_ms / dt_log))
        t = np.arange(n_steps, dtype=float) * dt_log

        v = np.asarray(log[self._voltage_label], dtype=float)
        i_net = None
        for c in QNET_CURRENTS:
            cur = np.asarray(log[self._current_labels[c]], dtype=float)
            i_net = cur if i_net is None else i_net + cur

        if i_net is None:
            i_net = np.zeros_like(v)

        if len(v) != len(t):
            raise TorsadeTwinError(
                "E_SOLVER",
                "Analysis-beat voltage log does not match the required grid.",
                detail=f"expected {len(t)} samples, got {len(v)}",
                http_status=503,
            )

        apd90, flags = compute_apd90(t, v)
        qnet, qnet_simpson = compute_qnet(t, i_net, cl_ms=cl_ms)
        diag = compute_diagnostics(t, v)

        return {
            "apd90_ms": apd90,
            "qnet_C_per_F": qnet,
            "qnet_simpson_C_per_F": qnet_simpson,
            "state": state,
            "nai_mM": state[nai_index],
            "v_rest_mV": diag["v_rest_mV"],
            "v_peak_mV": diag["v_peak_mV"],
            "dvdt_max_mV_per_ms": diag["dvdt_max_mV_per_ms"],
            "ra_flags": flags,
            "t": t,
            "v": v,
            "i_net": i_net,
        }

    def _convergence(self, prev, cur, state_names, eps_map):
        """C1-C4 per §4.4. Returns a diagnostics dict with pass/fail per criterion."""
        inf = float("inf")
        c1 = abs(cur["apd90_ms"] - prev["apd90_ms"]) if (
            cur["apd90_ms"] is not None and prev["apd90_ms"] is not None
        ) else inf
        c2 = 0.0
        for i, name in enumerate(state_names):
            s_cur = cur["state"][i]
            s_prev = prev["state"][i]
            eps = eps_map.get(name)
            if eps is None:
                eps = max(1.0, abs(s_cur))  # documented safe fallback
            denom = abs(s_cur) + eps
            if denom <= 0:
                denom = 1e-12
            c2 = max(c2, abs(s_cur - s_prev) / denom)
        c3 = abs(cur["nai_mM"] - prev["nai_mM"])
        q = cur["qnet_C_per_F"]
        c4 = abs(cur["qnet_C_per_F"] - prev["qnet_C_per_F"]) / abs(q) if q != 0 else inf
        pass_c1 = c1 < 0.05
        pass_c2 = c2 < 1e-4
        pass_c3 = c3 < 1e-3
        pass_c4 = c4 < 1e-3
        return {
            "converged": bool(all([pass_c1, pass_c2, pass_c3, pass_c4])),
            "c1_apd90_delta_ms": float(c1), "c1_pass": bool(pass_c1),
            "c2_max_state_rel": float(c2), "c2_pass": bool(pass_c2),
            "c3_nai_delta_mM": float(c3), "c3_pass": bool(pass_c3),
            "c4_qnet_rel": float(c4), "c4_pass": bool(pass_c4),
        }

    def _analysis_beat(self, sim, cl, offset, dt_log, beats_done, return_trace, conv, nai_index):
        """Run exactly one additional beat (the analysis beat) and use only that beat for
        the returned biomarkers/trace. Time is re-zeroed to the stimulus onset (§4.5)."""
        # The engine keeps Myokit time local to one cycle; physiological state
        # already represents all ``beats_done`` prior cycles.
        log = self._run_beat(sim, cl, dt_log)
        state = list(sim.state())
        beat = self._beat_from_log(log, state, nai_index, cl)
        t0 = beat["t"][0]
        t_rel = beat["t"] - t0
        ra = compute_ra_flags(t_rel, beat["v"], beat["apd90_ms"])
        result = SimulationResult(
            converged=True,
            beats_run=beats_done + 1,
            qnet_C_per_F=beat["qnet_C_per_F"],
            qnet_simpson_C_per_F=beat["qnet_simpson_C_per_F"],
            apd90_ms=beat["apd90_ms"],
            v_rest_mV=beat["v_rest_mV"],
            v_peak_mV=beat["v_peak_mV"],
            dvdt_max_mV_per_ms=beat["dvdt_max_mV_per_ms"],
            ra_flags=ra,
            convergence=conv,
            state_vector=state,
            diagnostics={"v_rest_mV": beat["v_rest_mV"], "v_peak_mV": beat["v_peak_mV"],
                          "dvdt_max_mV_per_ms": beat["dvdt_max_mV_per_ms"]},
        )
        if return_trace:
            result.trace_t_ms = list(t_rel)
            result.trace_v_mV = list(beat["v"])
            result.trace_i_net_A_per_F = list(beat["i_net"])
        return result

    def _set_channel_scale(self, sim, model, channel: str, f: float) -> None:
        # Literal baseline parameters in the vendored ORd-CiPA model.
        # Cell-type-specific conductance/permeability constants are derived from
        # these baseline parameters, so runtime scaling targets the literals.
        parameters = {
            "IKr": ["IKr.GKr_b"],
            "ICaL": ["ICaL.PCa_b"],
            "INa_peak": ["INa.GNa"],
            "INaL": ["INaL.GNaL_b"],
            "IKs": ["IKs.GKs_b"],
            "IK1": ["IK1.GK1_b"],
            "Ito": ["Ito.Gto_b"],
        }

        names = parameters.get(channel)
        if names is None:
            raise TorsadeTwinError(
                "E_MODEL_BINDING",
                f"No scaling binding defined for channel {channel}.",
                http_status=503,
            )

        for name in names:
            try:
                variable = model.get(name)
            except Exception as exc:
                raise TorsadeTwinError(
                    "E_MODEL_BINDING",
                    f"Scaling parameter missing for channel {channel}: {name}.",
                    detail=str(exc),
                    http_status=503,
                ) from exc

            if not variable.is_literal():
                raise TorsadeTwinError(
                    "E_MODEL_BINDING",
                    f"Scaling parameter is not runtime-adjustable for channel {channel}: {name}.",
                    http_status=503,
                )

        for name in names:
            # ``f`` is an unblocked fraction, not an absolute conductance.
            # A scale of 1.0 must preserve the vendored model parameter.
            baseline = float(model.get(name).rhs().eval())
            sim.set_constant(name, baseline * f)
