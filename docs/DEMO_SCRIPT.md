# Killer demo — exact 3-minute script (§22)

## Demo scenario (declared synthetic, `data/scenarios/demo_a.yaml`)

DEMO-A: dofetilide 1× + quinidine 1×, K+ 4.5 mM, CL 2000 ms, endo, standard.
DEMO-B: dofetilide 4× + quinidine 1×, K+ 3.2 mM, both drugs `discontinuable: false`.

## Minute-by-minute

| t | Step | Action | What is shown | Live or cached |
|---|---|---|---|---|
| 0:00 | 1. Baseline | load DEMO-A, click Simulate | AP trace, qNet, APD90, boundary line, VERIFIED chip | cached |
| 0:20 | 2. Compute margin | click Margin | M_signed = +1.8, unit convention, EXACT_AXIS | cached |
| 0:40 | 3. Change K+ | drag K+ 4.5 → 4.0 → 3.8 | sweep plot updates; margin shrinks in real time | cached grid |
| 1:00 | 4. Approach boundary | continue to 3.7 | margin → +0.3, amber "approaching boundary" (not a clinical warning) | cached grid |
| 1:10 | 5. Cross boundary | K+ = 3.6 | Phi < 0, "unsafe side of the model-defined boundary", crossing point annotated | cached grid |
| 1:25 | 6. Clinical score | open SCORE tab | Tisdale band constant across 4.5 → 3.6 while margin crosses; §13.4 verdict | cached |
| 1:45 | 7. Verify | open VERIFICATION tab | V-1..V-16 all PASS; toggle loose_NEGATIVE_CONTROL demo entry to show a FAILED result refused | cached (both) |
| 2:05 | 8. Mechanism | open MECHANISM tab | per-channel block table with IC50 + DOI; per-current charge contributions | cached |
| 2:20 | 9. Run Rescue | click Run rescue | all 15 actions with cost/Phi/feasible/credible; best action card (e.g. K+ → 4.4 mM, cost 0.8, post-rescue margin +1.1) | live on cached state (≤ 8 s) |
| 2:40 | 10. Best intervention | expand card | DISC_RESCUE, cost weights, post-rescue Phi and margin | live/cached |
| 2:50 | 11. Infeasible variant | load DEMO-B, click Rescue | INFEASIBLE_EXHAUSTIVE card: certificate wording, reason K_CEILING_BINDING, closest action, shortfall, DISC_INFEAS | cached |
| 3:00 | 12. Export | click Export JSON + PDF | provenance chain, hashes; re-import shows identical result_hash | live (≤ 3 s) |

## Precompute / cache / live split (§22.3)

- **Precomputed** (`scripts/build_demo_cache.py`, committed under `cache/demo/`): DEMO-A and DEMO-B baselines; K+ grid 5.4 → 3.0 mM in 0.1 mM steps; exposure grid 0.25×–4× in log2 quarter-steps; full margin results; full rescue tables; blind-spot sweeps; battery results for the demo config_hash.
- **Live during the demo**: rescue on the current cached state; report export; per-request verification gates.
- **Never live**: the 1000-beat cold solves, the heavy verification battery.
- **Latency ceilings**: any click ≤ 2 s from cache; live rescue ≤ 8 s; export ≤ 3 s; page load ≤ 1.5 s.

## Scientific honesty of the cached demo (§22.4)

Every cached value carries the same config_hash, result_hash and credibility state it had when computed, and the UI shows a `cached` badge with the computation timestamp. `scripts/verify_demo_cache.py` re-runs a random 10% sample live and fails if any cached number differs beyond tol_phi. No internet access is used at any point (A6).
