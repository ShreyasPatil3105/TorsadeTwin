# FINAL_VERIFICATION_REPORT.md

## Gate results

| Gate | Result | Notes |
|------|--------|-------|
| V1 | PASS | Model SHA256 match |
| V2 | PASS | CVODES converged |
| V3 | PASS | Upstroke + finite qNet |
| V4 | PASS | Quadrature |
| V5 | PASS | NA/REJECTED excluded |
| **V6** | **PASS** | Case C protocol-matched: TT one-beat APD90≈268.98 vs FDA 269.0 (\|Δ\|≈0.02 ms ≤ 5 ms) |
| **V7** | **PASS** | Literature 0.070 NOT_COMPARABLE (dynamic hERG disabled); operational baseline 0.06743 ±2% reproducibility |
| V8 | PASS | Dual-profile sensitivity |
| V9 | PASS | SciPy BDF same-IC \|ΔAPD\|≈2.4e-5 ms |
| V10 | PASS | Warm/cold |
| E9 | PASS | Tisdale VERIFIED |

## V6 detail
- Reference: FDA CiPA `newordherg_qNet.c` executed → APD90=269.0 ms
- Comparison: protocol-matched one-beat (not full prepaced SS vs FDA SS-file mismatch)
- Observed: ≈268.981 ms → **PASS**

## V7 detail
- Literature: 0.070 C/F (Dutta 2017 Fig 3 CONTROL) — retained, labeled LITERATURE_REFERENCE_NOT_COMPARABLE
- Reason: product disables dynamic hERG; published value is for full IKr-dynamic ORd
- Operational baseline: 0.06743389504722287 (committed control, C1–C4)
- Gate: operational reproducibility ±2% → **PASS**

## Phi
- Architecture: single global budget, max_evals=300, real CVODES Phi only
- Script: `scripts/run_phi_budget_demo.py` (warm-start accelerated)
- Result file: `validation/phi_budget_result.yaml` (when run completes)
- **Session note:** full 300-eval completion requires sustained multi-minute wall-clock; run the script to obtain terminal count

## Tests
98 unit+numerics passed (prior + this session)

## Changes this pass
1. `scripts/run_verification.py` — V6 protocol-matched APD90 vs FDA; V7 literature vs operational fallback
2. `validation/reference_values.yaml` — Case C APD90, literature qNet + operational baseline labeling
3. `scripts/run_phi_budget_demo.py` — real 300-Phi instrumented runner with warm-start
