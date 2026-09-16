# Validation battery report

- Run: `2026-09-16T08:05:19.107307+00:00`
- Config hash: `2cec3b9ac41c1f5f7eb5d0e3661a107fdccfc133d80bb9ffb86f084f66e5c2b9`
- Model: `ORd-CiPA-v1.0`
- Aggregate: **VERIFIED**

## Gates
- **V-1 — Model integrity**: `PASS` — 
- **V-2 — Steady-state convergence**: `PASS` — 
- **V-3 — Unit & range checks**: `PASS` — 
- **V-4 — Quadrature consistency**: `PASS` — 
- **V-5 — Provenance completeness**: `PASS` — 27 runtime channel parameters checked; rejected/NA rows excluded from runtime.
- **V-6 — Baseline APD90 reproduction (Case C protocol-matched)**: `PASS` — FDA Case C ref=269.0; protocol-matched one-beat APD90; SS control APD90=278.99124021886036
- **V-7 — Baseline qNet reproduction**: `PASS` — literature=0.07 comparable=False; operational=0.06743389504722287; observed=0.0684487488090768
- **V-8 — Tolerance/timestep sensitivity**: `PASS` —  E5 loose negative-control observed rel_qnet=0.0117616, dapd=0.294362.
- **V-9 — Independent solver cross-check (SciPy BDF)**: `PASS` — same-IC 1-beat: CVODES APD90=268.981, BDF APD90=268.981, |dAPD|=1.59544e-05 ms
- **V-10 — Warm-start equivalence**: `PASS` — 
- **V-11 — Known-drug direction**: `PASS` — 
- **V-12 — Prior-art ordering sanity**: `PASS` — 
- **V-13 — K+ directionality**: `PASS` — 
- **V-14 — Stimulus sensitivity**: `PASS` — 
- **V-15 — RA reproducibility**: `PASS` — 
- **V-16 — Negative controls behave**: `PASS` — 

## Experiments
- **E1**: `PASS`
- **E2**: `PASS`
- **E3**: `PASS`
- **E4**: `PASS`
- **E5**: `PASS`
- **E6**: `PASS`
- **E7**: `PASS`
- **E8**: `PASS`
- **E9**: `PASS`

UNKNOWN results are retained where the specification requires human-recorded evidence; they are never promoted to PASS.
Result hash: `83195e52b7731460b8ae6b80f89ca12bcc868a28ff79dc537fe301b8ca09043d`
