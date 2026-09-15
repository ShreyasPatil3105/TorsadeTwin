# TorsadeTwin

**Mechanistic Cardiac Safety Margin + Rescue Engine**

*TorsadeTwin turns an established human ventricular cell model into an inverse solver: it computes how far a modelled drug-and-electrolyte state sits from a model-defined repolarization-risk boundary, which variable is binding, and the smallest permitted intervention that restores a target margin — or reports that no permitted single action can.*

> **DISC_GLOBAL:** "Research prototype. In-silico model output only. Not clinically validated. Not for clinical decision-making."

**This is NOT a medical device.** TorsadeTwin is a mechanistic computational research prototype for hypothesis generation and methodology demonstration. The name "Twin" refers to a **cell-level mechanistic model twin of a declared synthetic state**, not a patient digital twin.

## What it does

1. Runs a vendored, published human ventricular myocyte model (ORd-CiPA v1.0, 2017) to steady state under a declared synthetic state.
2. Applies published multichannel IC50/Hill pore-block for a small, high-quality drug set.
3. Computes qNet (primary), APD90 (secondary), and a repolarization-abnormality annotation (tertiary, never definitional).
4. Computes a signed weighted distance from the current state to the model-defined qNet boundary Φ = 0.
5. Identifies the binding constraint by distance and by local normalized sensitivity.
6. Searches a finite, declared action set for the minimum-cost action restoring a target margin.
7. Reports exhaustive-domain infeasibility, or the weaker "no feasible action found", with the correct label.
8. Audits a categorical clinical score (Tisdale) against the mechanistic margin across a swept interval.
9. Attaches a credibility state (`VERIFIED` / `UNVERIFIED` / `FAILED`) to every result.
10. Emits a reproducible provenance record (parameter DOIs, model hash, solver version, config hash, result hash).

## What it explicitly does NOT do

Tissue/1D/2D/3D conduction, re-entry, spiral waves, whole-heart, ECG or QT reconstruction, population-of-models, PBPK, large drug libraries, ML/AI risk prediction, any LLM in the compute path, EHR/PHI integration, cloud services, dosing recommendations in clinical units, Mg²⁺, drug substitution search, pacing-CL margin axis, claims of clinical validation.

## Repository layout

See `docs/ARCHITECTURE.md` and §27 of `docs/SPEC.md` for the complete tree. Key directories:

- `backend/` — Python 3.11 FastAPI application (deterministic numerics, no LLM).
- `frontend/` — React + TypeScript + Vite single-page app (offline bundle, Plotly.js).
- `configs/` — frozen configuration (model, solver, protocol, domains, thresholds, margin, rescue, runtime).
- `data/` — drug parameters, drug registry, Tisdale score, synthetic scenarios.
- `models/` — vendored ORd-CiPA v1.0 artefact (`.mmt`) + provenance + audits.
- `validation/` — validation cases, reference values, battery results, golden files.
- `scripts/` — build, verification, demo-cache, integrity and offline-check scripts.
- `tests/` — the automated test suite (§26).
- `docs/` — spec, references, claims, demo script, judge QA, deviation register.

## Quick start

```bash
make setup          # create venv + install pinned deps (requires network ONCE)
make fetch-model    # ONE-TIME network fetch of the CellML artefact
make convert-model  # CellML -> models/ord_cipa_v1.mmt (committed), audits
make run            # uvicorn backend on http://127.0.0.1:8000
make frontend       # build + serve the frontend
make test           # run the CI gate test set
make battery        # run the §16 verification battery
make demo-cache     # precompute the demo grids
```

After `fetch-model` + `convert-model`, the system runs fully offline (A6).

## Data provenance gate

Every pharmacology value (`data/drug_parameters.csv`, `data/scores/tisdale.yaml`) and every reference value (`validation/reference_values.yaml`) must be **transcribed by a human** from the cited source, double-entered, and marked `verification_status: VERIFIED`. Until then rows stay `PLACEHOLDER` and the API returns `E_PROVENANCE_INCOMPLETE`. **No value is invented, recalled, estimated, interpolated or fabricated.** See `validation/transcription_log.md`.

## Claims

Approved and forbidden language is enforced by `test_copy_forbidden_phrases.py` across the whole repository. See `docs/CLAIMS.md` and §25 of `docs/SPEC.md`.
