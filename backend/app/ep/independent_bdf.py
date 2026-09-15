"""Independent SciPy BDF solve of the Myokit-exported Python RHS (SPEC §14 V-9).

Does NOT use myokit.Simulation / CVODES. Integrates models/generated/ord_rhs/sim.py
with scipy.integrate.solve_ivp(method='BDF') using the same physiological protocol
as the primary path (CL=2000 ms, stim offset 50 ms, duration 0.5 ms, amplitude -80).

APD90 is computed with the same biomarker engine as CVODES (§4.7).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

from .biomarkers import compute_apd90

ROOT = Path(__file__).resolve().parents[3]


def _load_generated():
    sim_path = ROOT / "models" / "generated" / "ord_rhs" / "sim.py"
    if not sim_path.exists():
        raise FileNotFoundError(f"Generated RHS missing: {sim_path}")
    name = "ord_rhs_sim"
    if name in sys.modules:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, sim_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_state(mod, y):
    (
        mod.c_membrane.v,
        mod.c_camk.CaMKt,
        mod.c_intracellular_ions.nai,
        mod.c_intracellular_ions.nass,
        mod.c_intracellular_ions.ki,
        mod.c_intracellular_ions.kss,
        mod.c_intracellular_ions.cass,
        mod.c_intracellular_ions.cansr,
        mod.c_intracellular_ions.cajsr,
        mod.c_intracellular_ions.cai,
        mod.c_ina.m, mod.c_ina.hf, mod.c_ina.hs, mod.c_ina.j, mod.c_ina.hsp, mod.c_ina.jp,
        mod.c_inal.mL, mod.c_inal.hL, mod.c_inal.hLp,
        mod.c_ito.a, mod.c_ito.iF, mod.c_ito.iS, mod.c_ito.ap, mod.c_ito.iFp, mod.c_ito.iSp,
        mod.c_ical.d, mod.c_ical.ff, mod.c_ical.fs, mod.c_ical.fcaf, mod.c_ical.fcas,
        mod.c_ical.jca, mod.c_ical.ffp, mod.c_ical.fcafp, mod.c_ical.nca,
        mod.c_ikr.IC1, mod.c_ikr.IC2, mod.c_ikr.C1, mod.c_ikr.C2, mod.c_ikr.O, mod.c_ikr.IO,
        mod.c_ikr.IObound, mod.c_ikr.Obound, mod.c_ikr.Cbound, mod.c_ikr.D,
        mod.c_iks.xs1, mod.c_iks.xs2, mod.c_ik1.xk1,
        mod.c_ryr.Jrelnp, mod.c_ryr.Jrelp,
    ) = [float(v) for v in y]
    mod.c_ikr.D = 1.0  # dynamic hERG disabled pathway


def _rhs_vector(mod):
    return np.array([
        mod.c_membrane.d_v,
        mod.c_camk.d_camkt,
        mod.c_intracellular_ions.d_nai,
        mod.c_intracellular_ions.d_nass,
        mod.c_intracellular_ions.d_ki,
        mod.c_intracellular_ions.d_kss,
        mod.c_intracellular_ions.d_cass,
        mod.c_intracellular_ions.d_cansr,
        mod.c_intracellular_ions.d_cajsr,
        mod.c_intracellular_ions.d_cai,
        mod.c_ina.d_m, mod.c_ina.d_hf, mod.c_ina.d_hs, mod.c_ina.d_j, mod.c_ina.d_hsp, mod.c_ina.d_jp,
        mod.c_inal.d_ml, mod.c_inal.d_hl, mod.c_inal.d_hlp,
        mod.c_ito.d_a, mod.c_ito.d_if, mod.c_ito.d_is, mod.c_ito.d_ap, mod.c_ito.d_ifp, mod.c_ito.d_isp,
        mod.c_ical.d_d, mod.c_ical.d_ff, mod.c_ical.d_fs, mod.c_ical.d_fcaf, mod.c_ical.d_fcas,
        mod.c_ical.d_jca, mod.c_ical.d_ffp, mod.c_ical.d_fcafp, mod.c_ical.d_nca,
        mod.c_ikr.d_ic1, mod.c_ikr.d_ic2, mod.c_ikr.d_c1, mod.c_ikr.d_c2, mod.c_ikr.d_o, mod.c_ikr.d_io,
        mod.c_ikr.d_iobound, mod.c_ikr.d_obound, mod.c_ikr.d_cbound, 0.0,  # D fixed
        mod.c_iks.d_xs1, mod.c_iks.d_xs2, mod.c_ik1.d_xk1,
        mod.c_ryr.d_jrelnp, mod.c_ryr.d_jrelp,
    ], dtype=float)


def run_independent_bdf_control(
    cl_ms: float = 2000.0,
    ko: float = 5.4,
    n_beats: int = 3,
    stim_offset_ms: float = 50.0,
    stim_duration_ms: float = 0.5,
    stim_amplitude: float = -80.0,
    rtol: float = 1e-8,
    atol: float = 1e-10,
    max_step: float = 0.1,
):
    """Integrate n_beats with SciPy BDF; return biomarkers on the last beat.

    Protocol matches configs/protocol.yaml (CL, stim offset/duration/amplitude).
    APD90 uses backend.app.ep.biomarkers.compute_apd90 (same as CVODES path).
    """
    from scipy.integrate import solve_ivp

    mod = _load_generated()
    mod.init()
    mod.c_ikr.D = 1.0
    mod.c_extracellular.ko = float(ko)
    mod.c_membrane.i_Stim_Start = float(stim_offset_ms)
    mod.c_membrane.i_Stim_Period = float(cl_ms)
    mod.c_membrane.i_Stim_PulseDuration = float(stim_duration_ms)
    mod.c_membrane.i_Stim_Amplitude = float(stim_amplitude)
    mod.c_membrane.i_Stim_End = 1e17
    mod.engine.time = 0.0

    y0 = np.array(mod.state(), dtype=float)
    y0[43] = 1.0  # IKr.D

    def rhs(t, y):
        mod.engine.time = float(t)
        _write_state(mod, y)
        mod.engine.update()
        return _rhs_vector(mod)

    t_end = float(n_beats) * float(cl_ms)
    sol = solve_ivp(
        rhs,
        (0.0, t_end),
        y0,
        method="BDF",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        dense_output=False,
    )
    if not sol.success:
        return {"ok": False, "message": sol.message, "v_peak": None, "apd90": None, "n_steps": 0}

    # Last beat only
    t0 = (n_beats - 1) * cl_ms
    mask = sol.t >= t0 - 1e-9
    t_beat = sol.t[mask] - t0
    v_beat = sol.y[0, mask]
    if len(t_beat) < 3:
        return {"ok": False, "message": "insufficient last-beat samples", "v_peak": None, "apd90": None}

    # Uniform grid for biomarker engine (same style as CVODES log)
    t_grid = np.arange(0.0, cl_ms + 1e-9, 0.1)
    v_grid = np.interp(t_grid, t_beat, v_beat)

    v_peak = float(np.max(v_grid))
    apd90 = None
    flags: list[str] = []
    try:
        apd90, flags = compute_apd90(t_grid, v_grid)
    except Exception as exc:
        return {
            "ok": False,
            "message": f"APD90 failed: {exc}",
            "v_peak": v_peak,
            "apd90": None,
            "n_steps": len(sol.t),
            "flags": [],
        }

    return {
        "ok": True,
        "v_peak": v_peak,
        "apd90": apd90,
        "n_steps": len(sol.t),
        "flags": flags,
        "message": "scipy BDF on exported RHS",
        "protocol": {
            "cl_ms": cl_ms,
            "ko": ko,
            "n_beats": n_beats,
            "stim_offset_ms": stim_offset_ms,
            "stim_duration_ms": stim_duration_ms,
            "stim_amplitude": stim_amplitude,
            "rtol": rtol,
            "atol": atol,
            "max_step": max_step,
        },
    }
