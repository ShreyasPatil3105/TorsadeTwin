# FINAL_BACKEND_REPORT.md — TorsadeTwin Backend

## Status summary

| Item | Result |
|------|--------|
| Model SHA256 | `99f4b927a15e879f4e88fa9cc6ca50c2a702c79f9dd346960927e823a0b6951c` **MATCH** |
| Myokit | 1.39.2 |
| CVODES | available (libsundials-dev) |
| Unit+numerics tests | **98 passed** |
| Data integrity | **OK** |
| Stimulus / max_step | 0.5 ms pulse, max_step_ms=0.1 (upstroke fixed) |
| V9 SciPy BDF | **PASS** (same-IC one-beat \|ΔAPD90\| ≈ 2.4e-5 ms) |
| V6/V7 independent refs | **FAIL** (no non-circular external numeric control from FDA C / Dutta text) |
| TOTAL_PHI_EVALUATIONS | **not completed to 300** in this environment (architecture supports it; wall-clock limited) |

## Architecture
- `backend/app/ep/` — Myokit CVODES simulate, biomarkers, block, independent BDF
- `backend/app/engines/` — Phi, margin, binding, rescue, blindspot
- `backend/app/data/` — drug registry with runtime NA/REJECTED exclusion
- `configs/` — solver, protocol, margin, domains, thresholds
- `models/ord_cipa_v1.mmt` — vendored ORd-CiPA v1.0
- `models/generated/ord_rhs/` — Myokit Python export for V9
- `scripts/run_verification.py` — V1–V10, E9 battery

## Scientific definitions (preserved)
- qNet primary, APD90 secondary
- boundary = 0.75 × qNet_control (modeling convention, not clinical cutoff)
- CL=2000 ms, Mg excluded, K→Ko 1:1
- dynamic hERG disabled (IKr.D=1 fixed)
- independent noncompetitive fractional multiplication for multi-drug
- INa_peak → INa.GNa

## V9 — Independent SciPy BDF (resolved)
**Root cause of prior failure:** Generated `Engine.update()` referenced `self.Jrel` instead of `c_ryr.Jrel`.

**Root cause of prior large ΔAPD:** Comparing multi-beat BDF from rest to fully prepaced CVODES (steady-state mismatch, not solver error).

**Fair protocol:** Same model initial conditions, one 2000 ms beat, same stimulus (offset 50 ms, duration 0.5 ms, amplitude −80), same `compute_apd90` biomarker engine.

| Solver | APD90 (ms) | Vpeak (mV) |
|--------|------------|------------|
| Myokit CVODES | 268.980922 | ~40.92 |
| SciPy BDF | 268.980898 | ~40.92 |
| \|ΔAPD90\| | **2.36e-5** | (< 2 ms SPEC) |

## V6 / V7 — Independent references (not fabricated)
- Dutta 2017 does not publish numeric control APD90/qNet for CL=2000 endo.
- FDA CiPA C (`newordherg_qNet.c`) could not be compiled/run here to extract metrics.
- Using this repo’s CVODES control as the “reference” is circular and rejected.
- **V6 = FAIL, V7 = FAIL** with documented limitation. No fabricated PASS.

## Phi budget
- Single global `_BudgetedPhi` with `max_evals=300`; `MarginResult.n_phi_evals` reports actual count.
- Full margin to exhaustion requires hundreds of real CVODES solves (hours with production prepace).
- Script `scripts/run_phi_budget_demo.py` provided for instrumented runs.
- **Completed terminal count of exactly 300 was not obtained in this session.**

## Files changed (this completion pass)
- `models/generated/ord_rhs/sim.py` — Engine.update Jrel binding patch
- `backend/app/ep/independent_bdf.py` — protocol-matched SciPy BDF + shared biomarker APD90
- `scripts/run_verification.py` — V9 fair same-IC comparison
- `validation/reference_values.yaml` — non-circular UNKNOWN/FAIL stance
- `scripts/run_phi_budget_demo.py` — instrumented Phi budget runner
- `FINAL_BACKEND_REPORT.md`, `FINAL_VERIFICATION_REPORT.md`

## Known scientific limitations
1. V6/V7 lack independent published/FDA-C numeric control targets.
2. Full 300-Phi verification battery not completed wall-clock in this environment.
3. Production prepace (1000 beats) is slow; demo path may use reduced prepace with explicit labeling.

## How to reproduce
```bash
pip install -r backend/requirements.txt   # myokit==1.39.2
# system: libsundials-dev
python -m pytest tests/unit tests/numerics -q
python scripts/verify_data_integrity.py
python -c "from backend.app.ep.independent_bdf import run_independent_bdf_control; print(run_independent_bdf_control())"
# V9 fair check is embedded in scripts/run_verification.py
```
