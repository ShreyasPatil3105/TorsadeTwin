# Architecture (§2)

## Dataflow (frozen)

```
[L1 INPUT LAYER]            scenario YAML / API request  -> validated StateSpec
         |
[L2 DRUG PARAMETER LAYER]   drug_parameters.csv + provenance -> ChannelBlockSpec
         |
[L3 PK / EXPOSURE LAYER]    exposure multipliers -> C_free per drug (nM)
         |
[L4 EP ENGINE]              vendored ORd-CiPA v1.0 + block -> steady-state beat
         |
[L5 BIOMARKER ENGINE]       qNet (primary), APD90 (secondary), RA flag (tertiary)
         |
[L6 MARGIN ENGINE]          Phi(x), signed margin M_hat, per-axis critical values
         |
[L7 RESCUE ENGINE]          finite action set A -> min-cost feasible action | infeasible
         |
[L8 BLIND-SPOT AUDITOR]     Tisdale sweep vs Phi sweep -> insensitivity intervals
         |
[L9 VERIFICATION ENGINE]    per-request gates + offline battery -> credibility state
         |
[L10 REPORT / PROVENANCE]   JSON + PDF, config hash, result hash, DOIs
         |
[L11 API]                   FastAPI, local, offline
         |
[L12 FRONTEND]              React + TS, local bundle, no CDN
```

Cross-cutting services: `cache` (SQLite-backed, keyed by canonical config hash), `hashing`, `logging`, `units`, `copy` (frozen strings).

## Component contracts

- **L1 Input layer** — validate and canonicalise every input; reject out-of-domain values before any solve. `StateSpec` (frozen Pydantic), `canonical_json`, `config_hash`. Failure modes: `E_UNKNOWN_DRUG`, `E_DOMAIN_K`, `E_DOMAIN_EXPOSURE`, `E_SCHEMA`.
- **L2 Drug parameter layer** — load `drug_parameters.csv` + `drug_registry.yaml`; refuse to serve any row lacking `source_doi` or with `verification_status != VERIFIED`. Failure: `E_PROVENANCE_INCOMPLETE` (startup abort).
- **L3 PK/exposure layer** — `C_free_d = exposure_multiplier_d × cmax_free_nM_d`; no compartmental PK in v1.0. Above `max_validated_multiple` → `OUT_OF_CALIBRATED_RANGE`.
- **L4 EP engine** — deterministic steady-state single-cell simulation with block applied (Myokit/CVODES). Failure: `E_SOLVER`, `E_NO_STEADY_STATE`, `E_NUMERICAL_INSTABILITY`.
- **L5 Biomarker engine** — qNet (primary), APD90 (secondary), RA flag (tertiary).
- **L6 Margin engine** — Φ evaluation, monotonicity pre-check, axis-wise critical values, weighted-distance minimisation (Stages A/B/C).
- **L7 Rescue engine** — exhaustive evaluation of the declared finite action set; minimum-cost feasible action; infeasibility classification.
- **L8 Blind-spot auditor** — Tisdale score across a swept variable; score-insensitivity intervals.
- **L9 Verification engine** — per-request fast gates + offline battery lookup; one credibility state.
- **L10 Report/provenance engine** — self-contained record; result hash; PDF.
- **L11 API** — FastAPI, uvicorn, localhost, synchronous endpoints with hard time budgets.
- **L12 Frontend** — React + TypeScript + Vite, offline bundle, Plotly.js for traces.

## Backend module map (§19.2)

```
backend/app/
  main.py                 FastAPI app factory, startup gates, routers
  config.py               loads configs/*.yaml into frozen dataclasses; computes config_hash
  copy/disclaimers.py     frozen user-facing strings (single source of truth)
  schemas/                common, simulate, margin, rescue, blindspot, verify, report
  data/                   drug_registry, scores, scenarios
  ep/                     model_loader, block, simulate, biomarkers
  engines/                phi, margin, binding, rescue, blindspot, verification
  services/               cache, hashing, provenance, report, jobs, errors, units
```

## Engine design note

The margin/rescue/binding/blindspot engines operate on a **Φ evaluator callable** (`StateSpec -> PhiEval`). In production this is backed by the EP engine + internally calibrated boundary; in tests it is an analytic surrogate (§26.3 rule 1). This is the frozen architecture — the inverse layer is consumed by the verification and integration streams without re-implementing Φ.
