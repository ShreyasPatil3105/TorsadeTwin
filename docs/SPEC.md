# TorsadeTwin Engineering Specification v1.0

_Mechanistic Cardiac Safety Margin + Rescue Engine — FROZEN IMPLEMENTATION CONTRACT (VMEDITHON 3.0)_

<callout icon="🔒" color="gray_bg">
	STATUS: FROZEN — IMPLEMENTATION CONTRACT. Version 1.0. Owner: Chief Scientist / Lead System Architect. Consumer: implementing coding model (DeepSeek V4 Flash) + student build team. This document is the SINGLE SOURCE OF TRUTH. The implementer must implement, not redesign. Any deviation requires a written entry in the Deviation Register (§0.3) and is otherwise forbidden.
</callout>
## §0 — PREAMBLE, SCOPE FREEZE, AND DEVIATION REGISTER
### 0.1 What this document is
An engineering contract for a **mechanistic in-silico cardiac safety margin and rescue engine**. It specifies exactly one cardiac model implementation, exactly one drug-block formulation, exactly one risk functional, exactly one margin algorithm, exactly one rescue algorithm, one credibility gate, one API, one UI, and one demo. Nothing in this document is a suggestion.
### 0.2 Non-negotiable engineering axioms
<table header-row="true">
<tr>
<td>#</td>
<td>Axiom</td>
</tr>
<tr>
<td>A1</td>
<td>No new physiology equations. All cell-model equations come from a published, publicly downloadable implementation, vendored unmodified except for documented conductance/parameter scaling.</td>
</tr>
<tr>
<td>A2</td>
<td>The novelty is the **inverse layer** (margin, binding constraint, minimum permitted rescue, infeasibility reporting). The cell model, qNet, Hill block, APD90 and Tisdale are **prior art** and must be cited as such everywhere they appear.</td>
</tr>
<tr>
<td>A3</td>
<td>Every displayed number carries a credibility state. `UNKNOWN` is never rendered as `PASS`.</td>
</tr>
<tr>
<td>A4</td>
<td>The primary decision functional is smooth and continuous (qNet-based). Repolarization abnormality / EAD detection is a **secondary, non-defining** output.</td>
</tr>
<tr>
<td>A5</td>
<td>No LLM participates in any computation. The backend is deterministic numerics.</td>
</tr>
<tr>
<td>A6</td>
<td>The system runs fully offline after a one-time asset fetch performed during the build.</td>
</tr>
<tr>
<td>A7</td>
<td>"Distance to a model-defined boundary" is never rendered, logged, exported or spoken as "probability of patient harm".</td>
</tr>
<tr>
<td>A8</td>
<td>Infeasibility is only called a *certificate* when the search domain is finite and was exhaustively evaluated with all evaluations credible.</td>
</tr>
</table>
### 0.3 Deviation Register (decisions made by the Chief Scientist that the implementer MUST honour)
These are resolutions of genuine tensions found in the requirements. They are frozen.
<table header-row="true">
<tr>
<td>ID</td>
<td>Tension found</td>
<td>Frozen resolution</td>
<td>Consequence the implementer must honour</td>
</tr>
<tr>
<td>**D1**</td>
<td>The requirement asks for a **simple pore-block (Hill) model**, but the CiPA-optimised ORd v1.0 model was calibrated and its published qNet thresholds derived using the **dynamic hERG drug-binding model** (Li et al. 2017), not Hill block on I\<sub\>Kr\</sub\>.</td>
<td>MVP uses **Hill/pore block on all channels including I\<sub\>Kr\</sub\>**, with the model's dynamic drug–hERG binding pathway explicitly disabled (drug concentration in the binding sub-model held at 0).</td>
<td>Absolute qNet values are **not** numerically comparable to published CiPA thresholds. Therefore the risk boundary is **internally calibrated to the model's own drug-free control** (§8.4). Published thresholds may only be shown as a *reference band*, labelled `LITERATURE_REFERENCE_NOT_COMPARABLE`. This must appear in the UI provenance panel and in the report.</td>
</tr>
<tr>
<td>**D2**</td>
<td>Requirement lists EAD detection, but forbids EAD from defining the margin.</td>
<td>Φ is defined purely on qNet. Repolarization-abnormality (RA) detection is a boolean annotation with its own credibility flag, and can only *downgrade* trust, never *define* the boundary.</td>
<td>No code path may compute the margin from RA.</td>
</tr>
<tr>
<td>**D3**</td>
<td>Requirement lists pacing cycle length as a physiological variable that might participate in margin optimisation, but qNet is protocol-defined at CL = 2000 ms.</td>
<td>CL is a **settable input** (affects APD90 and the AP trace) but is **excluded from the margin/rescue axes** in v1.0. Margin and rescue are always evaluated at CL = 2000 ms.</td>
<td>The UI must grey out CL as a margin axis and show the reason string `CL_EXCLUDED_PROTOCOL_BOUND`.</td>
</tr>
<tr>
<td>**D4**</td>
<td>Requirement asks about Mg²⁺.</td>
<td>**Excluded.** The selected model has no Mg²⁺-dependent conductance, no Mg²⁺ block of I\<sub\>K1\</sub\>/I\<sub\>Kr\</sub\> as a state-dependent term, and no published Mg²⁺ dose-response calibrated for it. Adding one would require inventing physiology → violates A1.</td>
<td>UI shows Mg²⁺ as `NOT MODELLED — no defensible pathway in the selected model`. No hidden Mg²⁺ parameter may exist in code or config.</td>
</tr>
<tr>
<td>**D5**</td>
<td>Requirement wants "patient state" without fake clinical data.</td>
<td>All scenarios are **synthetic, declared, non-identifiable regimen states**, stored in `data/scenarios/*.yaml` with a `synthetic: true` field. No PHI, no EHR, no real patient records.</td>
<td>The word "patient" in the UI is always rendered as "scenario" or "modelled state".</td>
</tr>
<tr>
<td>**D6**</td>
<td>Requirement wants combination pharmacology, which is scientifically uncertain.</td>
<td>Frozen assumption: **independent, non-competitive block per channel; fractional-block multiplication across drugs on the same channel** (§5.5). This is labelled an ASSUMPTION with an explicit sensitivity variant (additive-occupancy alternative) reported in the audit panel.</td>
<td>Never present the combination rule as validated. The report must contain the assumption ID `COMBO_RULE_INDEP_MULT_v1` and its sensitivity delta.</td>
</tr>
</table>
---
## §1 — PRODUCT DEFINITION
### 1.1 Identity
<table header-row="true">
<tr>
<td>Field</td>
<td>Value (frozen strings — use verbatim in UI and report)</td>
</tr>
<tr>
<td>Product name</td>
<td>**TorsadeTwin**</td>
</tr>
<tr>
<td>Subtitle</td>
<td>**Mechanistic Cardiac Safety Margin + Rescue Engine**</td>
</tr>
<tr>
<td>One-line pitch</td>
<td>*TorsadeTwin turns an established human ventricular cell model into an inverse solver: it computes how far a modelled drug-and-electrolyte state sits from a model-defined repolarization-risk boundary, which variable is binding, and the smallest permitted intervention that restores a target margin — or reports that no permitted single action can.*</td>
</tr>
<tr>
<td>Version</td>
<td>v1.0 (spec) / build tag `torsadetwin-0.1.0`</td>
</tr>
<tr>
<td>Category</td>
<td>Mechanistic computational research prototype (in-silico). **Not a medical device.**</td>
</tr>
</table>
### 1.2 The exact problem
Established drug-QT resources (CredibleMeds risk classes, Tisdale-type scores, interaction databases) return **categorical or ordinal** output. They answer *"is this risky?"*. They do not answer three engineering questions that a mechanistic model can answer:
1. **How much room is left?** (distance from the current modelled state to a defined boundary)
2. **What is holding the system?** (which single modelled variable is the binding constraint)
3. **What is the cheapest permitted move back?** (minimum-cost intervention restoring a target margin) — and, critically, **when is there no such move inside the permitted set?**
Secondary problem: categorical scores are **stepwise** in continuous physiology (e.g., a score item that triggers only at K⁺ ≤ 3.5 mM is flat across 3.6 → 4.5 mM), so they can be *insensitive* to a modelled variable over an interval where a mechanistic quantity moves substantially. TorsadeTwin quantifies that insensitivity without judging score correctness.
### 1.3 The exact user
Primary: **computational safety-pharmacology researcher / in-silico cardiac safety modeller / methods-focused reviewer** evaluating margin-and-rescue methodology.<br>Secondary: **hackathon judges and academic reviewers** assessing scientific defensibility.<br>Explicitly NOT a user: a clinician at the bedside making a treatment decision. The build must not be usable as bedside advice (no dosing output in mg, no patient identifiers, no "recommendation" verb — see §25).
### 1.4 The exact use case
> Load a declared synthetic scenario (drug set with free-concentration multipliers, extracellular K⁺, pacing CL). Simulate to steady state. Compute qNet, APD90, the signed safety margin to the model-defined boundary, the binding constraint and its critical value. Perturb K⁺ or exposure. Watch the margin move. Run the rescue solver over a finite declared action set. Read the minimum-cost feasible action, or the exhaustive-infeasibility result. Inspect the credibility gate and the provenance record. Export a reproducible JSON + PDF report whose result hash can be regenerated bit-for-bit.
### 1.5 Value proposition (frozen wording)
**"From categorical risk to computed distance, binding constraint, and minimum permitted rescue — with a numerical credibility gate that refuses to certify results it cannot verify."**
### 1.6 What the system does
1. Runs a vendored, published human ventricular myocyte model to steady state under a specified state.
2. Applies published multichannel IC50/Hill pore-block for a small, high-quality drug set.
3. Computes qNet (primary) and APD90 (secondary), plus RA/EAD annotation (tertiary).
4. Computes a **signed weighted distance** from the current state to the model-defined qNet boundary Φ = 0.
5. Identifies the **binding constraint** by distance and by local normalized sensitivity.
6. Searches a **finite, declared action set** for the minimum-cost action restoring a target margin.
7. Reports **exhaustive-domain infeasibility**, or the weaker "no feasible action found", with the correct label.
8. Audits a categorical clinical score (Tisdale) against the mechanistic margin across a swept interval and reports **score insensitivity intervals**.
9. Attaches a credibility state (`VERIFIED` / `UNVERIFIED` / `FAILED`) to every result.
10. Emits a reproducible provenance record (parameter DOIs, model hash, solver version, config hash, result hash).
### 1.7 What the system explicitly does NOT do
Tissue/1D/2D/3D conduction, re-entry, spiral waves, whole-heart, ECG or QT-interval reconstruction, population-of-models as a core feature, PBPK, large drug libraries, ML/AI risk prediction, chatbot or LLM in the compute path, EHR/PHI integration, mobile app, cloud services, dosing recommendations in clinical units, Mg²⁺ (D4), drug substitution search (§11.6), pacing-CL margin axis (D3), claims of clinical validation.
### 1.8 Research/demo framing (must appear on first screen)
> TorsadeTwin is an in-silico research prototype built on published cardiac electrophysiology and published ion-channel pharmacology. It computes distances to a **model-defined** repolarization-risk boundary. It does not predict Torsade de Pointes in any individual, has no clinical-validation evidence, and must not be used for clinical decision-making.
### 1.9 Disclaimer strings (frozen; single source `backend/app/copy/disclaimers.py`)
<table header-row="true">
<tr>
<td>Key</td>
<td>String</td>
</tr>
<tr>
<td>`DISC_GLOBAL`</td>
<td>Frozen global research disclaimer; canonical value in `backend/app/copy/disclaimers.py`.</td>
</tr>
<tr>
<td>`DISC_MARGIN`</td>
<td>"Margin = weighted distance in modelled-state space to the model-defined qNet boundary. It is NOT a probability of clinical harm."</td>
</tr>
<tr>
<td>`DISC_RESCUE`</td>
<td>"Rescue = minimum-cost element of a declared finite action set that restores the target margin **in this model**. It is not a treatment recommendation."</td>
</tr>
<tr>
<td>`DISC_INFEAS`</td>
<td>"Exhaustive over the declared finite action set only. Says nothing about actions outside that set."</td>
</tr>
<tr>
<td>`DISC_SCORE`</td>
<td>"Comparison shows the score's insensitivity to a modelled variable over an interval. It does not establish that the score is incorrect."</td>
</tr>
<tr>
<td>`DISC_UNVERIFIED`</td>
<td>"NOT TRUSTWORTHY — numerical credibility checks did not pass. Result shown for debugging only."</td>
</tr>
</table>
### 1.10 Core differentiator
A **constrained inverse solver** wrapped around an established forward cell model: margin → binding constraint → minimum permitted rescue → exhaustive-domain infeasibility, gated by numerical verification. Forward simulators (prior art) stop at the first arrow.
### 1.11 Old system vs new TorsadeTwin system
<table header-row="true">
<tr>
<td>Dimension</td>
<td>Old system (CredibleMeds / Tisdale / interaction DBs / plain forward simulators)</td>
<td>New TorsadeTwin system</td>
</tr>
<tr>
<td>Output type</td>
<td>Category / ordinal score / single forward biomarker</td>
<td>Signed continuous distance to a model-defined boundary</td>
</tr>
<tr>
<td>Question answered</td>
<td>"Is this risky?"</td>
<td>"How far from the boundary, which variable binds, what is the smallest permitted move back?"</td>
</tr>
<tr>
<td>Direction of computation</td>
<td>Forward only (state → risk)</td>
<td>Forward **plus inverse** (risk → required state change)</td>
</tr>
<tr>
<td>Sensitivity to continuous physiology</td>
<td>Stepwise / threshold-driven / absent</td>
<td>Continuous in K⁺ and log-exposure</td>
</tr>
<tr>
<td>Actionability</td>
<td>None (or expert judgement)</td>
<td>Minimum-cost action over a declared finite permitted set</td>
</tr>
<tr>
<td>Behaviour when nothing works</td>
<td>Silent / unspecified</td>
<td>Explicit exhaustive-domain infeasibility result with the binding reason</td>
</tr>
<tr>
<td>Numerical trust</td>
<td>Usually implicit</td>
<td>Explicit `VERIFIED / UNVERIFIED / FAILED` gate on every result</td>
</tr>
<tr>
<td>Reproducibility</td>
<td>Rarely hash-traceable</td>
<td>Config hash + result hash + parameter DOIs on every export</td>
</tr>
<tr>
<td>Claim scope</td>
<td>Clinical risk labelling</td>
<td>Model-defined boundary only; no clinical prediction</td>
</tr>
</table>
---
## §2 — COMPLETE SYSTEM ARCHITECTURE
### 2.1 Dataflow (frozen)
```plain text
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
### 2.2 Component contracts
#### L1 — Input layer
- **Responsibility:** validate and canonicalise every input; reject out-of-domain values before any solve.
- **Inputs:** API JSON or scenario YAML: `drugs[{id, exposure_multiplier]`, `k_o_mM`, `cl_ms`, `cell_type`, `solver_profile`, `seed?`.
- **Outputs:** `StateSpec` (frozen Pydantic model), plus `canonical_json` and `config_hash`.
- **Dependencies:** drug registry (L2), `configs/domains.yaml`.
- **Algorithm:** schema validation → domain clamp check (hard reject, never silent clamp) → canonical JSON serialisation (sorted keys, fixed float formatting `%.10g`) → SHA-256.
- **Failure modes:** unknown drug id → `E_UNKNOWN_DRUG`; out-of-range K⁺ → `E_DOMAIN_K`; multiplier \> max → `E_DOMAIN_EXPOSURE`; malformed body → `E_SCHEMA`.
- **Tests:** `test_inputs_validation.py` (every reject path, canonical-hash stability under key reordering and float formatting).
#### L2 — Data / drug parameter layer
- **Responsibility:** load `drug_parameters.csv` + `drug_registry.yaml`; refuse to serve any row lacking `source_doi` or with `verification_status != VERIFIED`.
- **Inputs:** CSV/YAML on disk.
- **Outputs:** `DrugRecord` objects, per-channel `(IC50_nM, hill, source_doi)`, `cmax_free_nM`, `discontinuable`, `qt_risk_class_manual?`.
- **Algorithm:** parse → unit check (all IC50 in nM, Hill dimensionless, 0.5 ≤ h ≤ 3.0) → provenance completeness gate → freeze into an immutable registry.
- **Failure modes:** missing DOI → startup abort `E_PROVENANCE_INCOMPLETE`; NaN IC50 → row served as `no block on that channel` **only if** explicitly encoded `NA` with `na_reason`; otherwise abort.
- **Tests:** `test_drug_registry.py`, `test_negative_control_bad_drug_csv.py`.
#### L3 — PK / exposure layer
- **Responsibility:** convert declared exposure into free concentration.
- **Frozen MVP behaviour:** **accept C_free directly** via `exposure_multiplier × cmax_free_nM` (§6). No compartmental PK in v1.0.
- **Outputs:** `{drug_id: C_free_nM}`.
- **Failure modes:** `C_free` above `max_validated_multiple` (default 25× C_max) → result tagged `OUT_OF_CALIBRATED_RANGE`, credibility ≤ `UNVERIFIED`.
- **Tests:** `test_exposure_layer.py`.
#### L4 — Electrophysiology engine
- **Responsibility:** deterministic steady-state single-cell simulation with block applied.
- **Inputs:** `StateSpec`, `ChannelBlockSpec`, solver profile.
- **Outputs:** final-beat trace `(t, V, currents…)`, converged state vector, convergence diagnostics.
- **Dependencies:** Myokit + CVODES; vendored `.mmt`.
- **Algorithm:** §4.
- **Failure modes:** CVODE failure → `E_SOLVER`; non-convergence → `E_NO_STEADY_STATE`; V drift/blow-up → `E_NUMERICAL_INSTABILITY`.
- **Tests:** `test_ep_engine.py`, `test_steady_state.py`, `test_reproducibility.py`.
#### L5 — Biomarker engine
- **Responsibility:** compute qNet, APD90, RA flag from the final beat only.
- **Algorithm:** §4.7–4.9.
- **Failure modes:** APD90 undefined (no 90% recovery) → `APD90 = null`, `RA_flag = REPOL_FAILURE`, credibility ≤ `UNVERIFIED` unless RA gates pass.
- **Tests:** `test_biomarkers.py` (synthetic analytic traces with known APD90 and known integral).
#### L6 — Margin engine
- **Responsibility:** Φ evaluation, monotonicity pre-check, axis-wise critical values, weighted-distance minimisation.
- **Algorithm:** §9.
- **Failure modes:** non-monotone Φ → `NON_MONOTONIC` flag + multi-root reporting; budget exceeded → `M_STATUS = BUDGET_EXCEEDED`.
- **Tests:** `test_margin_engine.py`, `test_margin_monotonicity.py`, `test_margin_regression.py`.
#### L7 — Rescue engine
- **Responsibility:** exhaustive evaluation of the declared finite action set; minimum-cost feasible action; infeasibility classification.
- **Algorithm:** §11–§12.
- **Failure modes:** any action evaluation not credible → certificate downgraded to `INCOMPLETE_SEARCH`.
- **Tests:** `test_rescue_engine.py`, `test_infeasibility_certificate.py`.
#### L8 — Blind-spot auditor
- **Responsibility:** compute Tisdale score across a swept variable and detect intervals where the score is constant while Φ changes by more than a threshold.
- **Algorithm:** §13.
- **Failure modes:** missing score inputs → item scored `UNKNOWN`, score reported as an interval `[min, max]`, never a point value.
- **Tests:** `test_blindspot_auditor.py`, `test_tisdale_scoring.py`.
#### L9 — Verification / credibility engine
- **Responsibility:** run per-request fast gates; look up the offline battery result for the current config hash; combine into one credibility state.
- **Algorithm:** §14.
- **Failure modes:** battery result missing → `UNVERIFIED` (never `VERIFIED`).
- **Tests:** `test_verification_engine.py`, `test_negative_controls.py`.
#### L10 — Report / provenance engine
- **Responsibility:** assemble a self-contained record; compute the result hash; render PDF.
- **Outputs:** `report.json`, `report.pdf`.
- **Failure modes:** any missing provenance field → refuse to emit (`E_PROVENANCE_INCOMPLETE`).
- **Tests:** `test_report_provenance.py`, `test_result_hash_stability.py`.
#### L11 — API
- FastAPI, uvicorn, [localhost](http://localhost), synchronous endpoints with hard time budgets and a single background worker pool. §20.
#### L12 — Frontend
- React + TypeScript + Vite, offline bundle, Plotly.js for traces. §21.
---
## §3 — MODEL SELECTION (FROZEN — DO NOT SUBSTITUTE)
### 3.1 Primary model (mandatory)
<table header-row="true">
<tr>
<td>Field</td>
<td>Value</td>
</tr>
<tr>
<td>Implementation family</td>
<td>**O'Hara–Rudy dynamic (ORd) lineage, CiPA-optimised variant: "ORd-CiPA v1.0 (2017)"**</td>
</tr>
<tr>
<td>Physiology source</td>
<td>O'Hara T, Virág L, Varró A, Rudy Y. *Simulation of the undiseased human cardiac ventricular action potential.* PLoS Comput Biol 2011;7(5):e1002061. doi:10.1371/journal.pcbi.1002061</td>
</tr>
<tr>
<td>Optimised-conductance source</td>
<td>Dutta S, Chang KC, Beattie KA, Sheng J, Tran PN, Wu WW, et al. *Optimization of an in silico cardiac cell model for proarrhythmia risk assessment.* Front Physiol 2017;8:616. doi:10.3389/fphys.2017.00616</td>
</tr>
<tr>
<td>Dynamic hERG-binding source (present in file, DISABLED per D1)</td>
<td>Li Z, Dutta S, Sheng J, Tran PN, Wu W, et al. Circ Arrhythm Electrophysiol 2017;10:e004628. doi:10.1161/CIRCEP.116.004628</td>
</tr>
<tr>
<td>Preferred artefact</td>
<td>**CellML: ****`ohara_rudy_cipa_v1_2017.cellml`**, Physiome Model Repository exposure `https://models.cellml.org/e/5a0` (workspace `/workspace/4e4`)</td>
</tr>
<tr>
<td>Independent cross-check artefact</td>
<td>FDA reference C implementation `AP_simulation/models/newordherg_qNet.c`, `https://github.com/FDA/CiPA` (GPL-3.0)</td>
</tr>
<tr>
<td>Runtime host</td>
<td>**Myokit** (`.mmt` produced by Myokit's CellML importer, then vendored)</td>
</tr>
</table>
**Why this exact artefact:** (a) it is the CiPA-lineage model on which qNet was defined, so the primary functional is not invented; (b) the Physiome exposure is publicly downloadable without credentialing; (c) that CellML version was converted to Chaste C++ and **checked against the FDA reference code**, giving an independent numerical reference for §14 V-9; (d) Myokit gives CVODES stiff integration, exact pacing protocols, state export/import for warm starts, and a Python export path for cross-solver verification.
### 3.2 Loading procedure (frozen)
1. Build-time script `scripts/fetch_model.py` downloads the CellML file to `models/vendor/ohara_rudy_cipa_v1_2017.cellml`, records SHA-256 in `models/vendor/CHECKSUMS.txt`, and stores the source URL + retrieval date in `models/vendor/PROVENANCE.yaml`.
2. `scripts/convert_model.py` imports it via `myokit.formats.cellml` and writes `models/ord_cipa_v1.mmt`. The `.mmt` is **committed** to the repository. After this step the system never needs the network (A6).
3. `models/ord_cipa_v1.mmt` is loaded read-only at runtime. All drug and electrolyte effects are applied **in code via ****`myokit.Simulation.set_constant()`**, never by editing the `.mmt`.
4. Any `.mmt` whose SHA-256 does not match `models/CHECKSUMS.txt` → startup abort `E_MODEL_HASH_MISMATCH`.
5. Required `.mmt` label bindings, asserted at startup (`test_model_bindings.py`): membrane potential, stimulus current, `extracellular.ko`, and the six qNet currents `INaL, ICaL, IKr, IKs, IK1, Ito`. Missing label → `E_MODEL_BINDING`.
### 3.3 Conductance scaling (transcribe exactly, do not re-derive)
The optimised IKr-dyn ORd multipliers published in Dutta 2017 (Table: original → optimised) are:
<table header-row="true">
<tr>
<td>Current</td>
<td>Optimised scaling factor</td>
</tr>
<tr>
<td>I\<sub\>Kr\</sub\></td>
<td>1.013</td>
</tr>
<tr>
<td>I\<sub\>Ks\</sub\></td>
<td>1.870</td>
</tr>
<tr>
<td>I\<sub\>K1\</sub\></td>
<td>1.698</td>
</tr>
<tr>
<td>I\<sub\>CaL\</sub\></td>
<td>1.007</td>
</tr>
<tr>
<td>I\<sub\>NaL\</sub\></td>
<td>2.661</td>
</tr>
</table>
If and only if the vendored CellML already embeds these factors (it should, being the CiPA v1.0 exposure), the code must **not** apply them again. `scripts/convert_model.py` prints the model's effective conductance constants; the implementer records the outcome in `models/SCALING_AUDIT.md` and sets `configs/model.yaml: apply_dutta_scaling: false|true` accordingly. Double-scaling is a build-blocking bug; `test_model_scaling_audit.py` asserts consistency with the recorded audit.
### 3.4 Fallback model (only on documented primary failure)
<table header-row="true">
<tr>
<td>Field</td>
<td>Value</td>
</tr>
<tr>
<td>Fallback</td>
<td>**ORd 2011 endocardial**, Myokit example file `ord-2011.mmt` ([myokit.org/examples](http://myokit.org/examples)), physiology per O'Hara 2011</td>
</tr>
<tr>
<td>Trigger</td>
<td>CellML import fails, or model-hash/binding assertions cannot be satisfied, and the failure is recorded in `docs/FALLBACK_INVOKED.md`</td>
</tr>
<tr>
<td>Consequence</td>
<td>`model_id = "ORd2011-endo"` propagates into every result, hash and report; the UI shows a persistent banner `FALLBACK MODEL — qNet boundary recalibrated to this model's own control`; all reference values in `validation/reference_values.yaml` must be re-recorded for this model before anything may reach `VERIFIED`</td>
</tr>
<tr>
<td>Caveat to display</td>
<td>ORd-2011 is known to be more permissive to EAD/repolarization-instability behaviour under strong I\<sub\>Kr\</sub\> block than the CiPA-optimised variant; RA annotations are therefore reported with `model_caveat: ORD2011_EAD_SENSITIVITY`</td>
</tr>
</table>
Switching model silently is forbidden (A1, RULE 3). Only `configs/model.yaml: model_id` selects it, and only two values are legal: `ORd-CiPA-v1.0` (default) and `ORd2011-endo`.
### 3.5 Model-specific caveats to carry in the UI
1. Endocardial cell type only in v1.0 (`cell_type: endo`, frozen). Epi/mid are out of scope.
2. Single cell, no electrotonic coupling → no re-entry claim is possible (§25).
3. The dynamic hERG binding pathway exists in the file and is **disabled**; the disable action is asserted by `test_herg_dynamic_disabled.py`.
---
## §4 — CARDIAC MODEL EXECUTION (FROZEN NUMERICS)
### 4.1 Solver
<table header-row="true">
<tr>
<td>Setting</td>
<td>Value (`solver_profile: standard`)</td>
</tr>
<tr>
<td>Integrator</td>
<td>Myokit `myokit.Simulation` (CVODES, BDF, stiff, adaptive)</td>
</tr>
<tr>
<td>Relative tolerance</td>
<td>`1e-8`</td>
</tr>
<tr>
<td>Absolute tolerance</td>
<td>`1e-10`</td>
</tr>
<tr>
<td>Max internal step</td>
<td>`1.0` ms</td>
</tr>
<tr>
<td>Log sampling for analysis</td>
<td>fixed `dt_log = 0.1` ms on the final beat (`log_interval`)</td>
</tr>
<tr>
<td>Stimulus</td>
<td>protocol-driven, amplitude `-80` A/F, duration `0.5` ms, offset `50` ms into each cycle, period = CL</td>
</tr>
<tr>
<td>Determinism</td>
<td>no randomness anywhere; `PYTHONHASHSEED=0`; float64 only</td>
</tr>
</table>
Additional profiles (used only by the verification battery, §14): `tight` (rtol 1e-10, atol 1e-12, max step 0.05 ms), `loose_NEGATIVE_CONTROL` (rtol 1e-4, atol 1e-6, max step 5 ms — must FAIL the gates), `coarse_log` (dt_log 1.0 ms).
### 4.2 State variables
Whatever the vendored `.mmt` defines (ORd-CiPA v1.0: membrane potential; Na⁺/K⁺/Ca²⁺ concentrations in myoplasm, subspace and SR; INa/INaL/ICaL/Ito/IKr/IKs gating variables; CaMK activation; and the hERG dynamic-binding occupancy states, held drug-free). The implementer must not add, remove or rename state variables. The full ordered list is dumped at build time to `models/STATE_VARIABLES.md` by `scripts/convert_model.py` and asserted by `test_model_state_list.py`.
### 4.3 Pacing
<table header-row="true">
<tr>
<td>Setting</td>
<td>Value</td>
</tr>
<tr>
<td>Default CL</td>
<td>**2000 ms** (CiPA qNet protocol; mandatory for qNet, margin, rescue)</td>
</tr>
<tr>
<td>Settable CL range (APD90/trace only)</td>
<td>500–2000 ms, step 100 ms</td>
</tr>
<tr>
<td>Pre-pace beats</td>
<td>`n_prepace = 1000` at the target CL</td>
</tr>
<tr>
<td>Max additional beats if not converged</td>
<td>`n_extra_max = 1000`, in blocks of 100</td>
</tr>
</table>
### 4.4 Steady-state convergence criteria (all must hold on the last block)
```plain text
C1  |APD90(n) - APD90(n-1)|                  < 0.05 ms
C2  max_i |s_i(n) - s_i(n-1)| / (|s_i(n)| + eps_i) < 1e-4     over all state variables
C3  |[Na+]i(n) - [Na+]i(n-1)|                < 1e-3 mM
C4  |qNet(n) - qNet(n-1)| / |qNet(n)|        < 1e-3
```
`eps_i` = per-variable scale from `configs/state_scales.yaml` (generated once from a control run; committed). If C1–C4 fail after `n_prepace + n_extra_max`, return `E_NO_STEADY_STATE`, credibility `FAILED`, and never emit a margin.
### 4.5 Final-beat selection (exact)
After convergence, run **one additional beat** with `log_interval = dt_log`, logging from the stimulus onset of that beat (`t0`) to `t0 + CL`. That beat — and only that beat — is the analysis beat. Time is re-zeroed to `t - t0`.
### 4.6 Warm start and caching
- **Cache key:** `sha256(canonical(model_id, model_hash, solver_profile, cell_type, CL, K_o, block_vector_rounded_1e-6))`.
- Cache stores: converged state vector, qNet, APD90, RA flag, diagnostics, code version. Backend: SQLite (`cache/torsadetwin.sqlite`) + JSON blobs.
- **Warm start:** initialise from the cached state of the nearest neighbour in the same (CL, cell_type) family, distance = weighted L1 over `(K_o, log10 block factors)`. Then still run `n_warm = 200` beats and require C1–C4.
- **Mandatory equivalence gate (V-10):** for the demo scenarios, warm-started results must match cold-started (1000-beat) results within `|ΔqNet|/qNet < 0.5%` and `|ΔAPD90| < 0.5 ms`; otherwise warm start is disabled globally (`configs/runtime.yaml: warm_start: false`).
### 4.7 APD90 (exact algorithm)
```plain text
Input: final-beat arrays t[0..N-1] (ms, uniform 0.1 ms), V[0..N-1] (mV)
1. t_act   = argmax(dV/dt) computed by central differences   -> activation time
2. V_peak  = max(V[t >= t_act])
3. V_rest  = V[N-1]                     (end-of-cycle potential, the diastolic baseline)
4. V_90    = V_peak - 0.90 * (V_peak - V_rest)
5. t_90    = first t > t_peak where V crosses V_90 downward,
             refined by LINEAR INTERPOLATION between the bracketing samples
6. APD90   = t_90 - t_act
Errors:
  - no downward crossing of V_90 before end of cycle -> APD90 = null, RA_flag |= REPOL_FAILURE
  - V_peak < 0 mV                                    -> APD90 = null, error E_NO_UPSTROKE
  - more than one downward crossing of V_90           -> RA_flag |= MULTI_CROSSING (APD90 = first crossing)
```
### 4.8 qNet (exact algorithm) — see §8
### 4.9 Mandatory biomarker set (exactly these; adding more is forbidden in v1.0)
<table header-row="true">
<tr>
<td>Biomarker</td>
<td>Role</td>
<td>Definition</td>
</tr>
<tr>
<td>**qNet**</td>
<td>PRIMARY (defines Φ)</td>
<td>§8.1</td>
</tr>
<tr>
<td>**APD90**</td>
<td>SECONDARY (display, convergence check, verification)</td>
<td>§4.7</td>
</tr>
<tr>
<td>**RA flag**</td>
<td>TERTIARY (annotation only, D2)</td>
<td>§8.6</td>
</tr>
<tr>
<td>`V_rest`, `V_peak`, `dVdt_max`</td>
<td>diagnostics for the credibility gate only</td>
<td>standard</td>
</tr>
<tr>
<td>`[Na+]i`, `[Ca]i_peak`</td>
<td>convergence diagnostics only</td>
<td>last-beat values</td>
</tr>
</table>
qInward, cqInward, triangulation, APD50, CTD and "instability indices" are **excluded** from v1.0 (RULE 4).
### 4.10 Reproducibility requirements
Same inputs + same `config_hash` + same code version ⇒ bit-identical `result_hash`. Enforced by `test_reproducibility.py` (two runs in-process) and `test_result_hash_stability.py` (golden hashes in `validation/golden/`). Floats are serialised with `repr()`-stable formatting `%.12e` before hashing. Any nondeterminism (thread-count-dependent reductions, dict ordering, wall-clock in hashed payloads) is a build-blocking bug.
---
## §5 — DRUG MODEL
### 5.1 Channel panel (frozen, 6 targets)
`IKr (hERG)`, `ICaL (Cav1.2)`, `INa_peak (Nav1.5 peak)`, `INaL (Nav1.5 late)`, `IKs (KCNQ1/minK)`, `Ito (Kv4.3)`, plus optional `IK1 (Kir2.1)` if the source reports it. Any channel with no data is encoded `NA` with `na_reason` and contributes **zero block** — and the result carries `partial_panel: [channel…]`.
### 5.2 `drug_parameters.csv` schema (frozen, one row per drug × channel)
```plain text
drug_id,drug_name,channel,ic50_nM,hill,ic50_ci_low_nM,ic50_ci_high_nM,n_replicates,
assay,temperature_C,source_citation,source_doi,source_table,units_check,
na_reason,verification_status,transcribed_by,transcribed_on
```
Rules: `units_check` must equal `IC50_nM|hill_dimensionless`; `verification_status ∈ {VERIFIED, PLACEHOLDER, REJECTED}`; the loader **refuses to serve** any row that is not `VERIFIED`; `hill` default 1.0 only if the source reports it as such (never silently).
### 5.3 `drug_registry.yaml` schema (one entry per drug)
```yaml
- drug_id: dofetilide
  drug_name: Dofetilide
  cmax_free_nM: 2.0                 # CiPA training-set free Cmax; source_doi required
  cmax_source_doi: "10.1002/cpt.1184"
  max_validated_multiple: 25        # simulate above this -> OUT_OF_CALIBRATED_RANGE
  discontinuable: false             # may the rescue engine set exposure to 0?
  dose_steps: [1.0, 0.75, 0.5, 0.25]
  cipa_training_risk_label: high    # PRIOR-ART LABEL, display only, never an input to Phi
  qt_risk_class_manual: null        # CredibleMeds class, manually entered, NOT redistributed
  notes: ""
```
### 5.4 Pore-block equation (frozen — simple Hill/pore block, prior art)
For drug *d*, channel *c*, free concentration `C_d` (nM):
```plain text
block fraction    b_{d,c} = 1 / (1 + (IC50_{d,c} / C_d)^{h_{d,c}})        , C_d > 0
unblocked frac.   f_{d,c} = 1 - b_{d,c} = 1 / (1 + (C_d / IC50_{d,c})^{h_{d,c}})
applied as        G_c_effective = G_c_nominal * F_c
```
Implementation: `F_c` is written to the model constant that multiplies the channel's maximal conductance via `set_constant()`. No current equation is edited (A1).
### 5.5 Combination rule (frozen ASSUMPTION `COMBO_RULE_INDEP_MULT_v1`)
```plain text
F_c = PRODUCT over drugs d of f_{d,c}          (independent, non-competitive block)
```
**Mandatory honesty requirements:**
1. Label in UI and report: *"Assumption: independent non-competitive block, fractional effects multiplied per channel. Not experimentally validated for these combinations."*
2. A sensitivity variant `COMBO_RULE_ADDITIVE_OCC_v1` (`b_c = min(1, Σ_d b_{d,c})`) must be computed for the audit panel; report `ΔqNet` and `Δmargin` between rules. If the two rules place the state on **opposite sides** of the boundary, the result's credibility is capped at `UNVERIFIED` with reason `COMBO_RULE_SENSITIVE`.
3. Neither rule may be described as proven.
### 5.6 MVP drug set (frozen: 6 drugs + control)
Chosen for strong published multichannel data and a spread of CiPA prior-art labels, including the mechanistically important "strong hERG block but low risk" case (verapamil).
<table header-row="true">
<tr>
<td>drug_id</td>
<td>CiPA prior-art label</td>
<td>Free C_max (nM) as published in the CiPA training set</td>
<td>Why included</td>
</tr>
<tr>
<td>`dofetilide`</td>
<td>high</td>
<td>2</td>
<td>canonical selective I\<sub\>Kr\</sub\> blocker; direction test</td>
</tr>
<tr>
<td>`sotalol`</td>
<td>high</td>
<td>14690</td>
<td>high-risk, high-concentration case</td>
</tr>
<tr>
<td>`quinidine`</td>
<td>high</td>
<td>3237</td>
<td>multichannel high-risk</td>
</tr>
<tr>
<td>`cisapride`</td>
<td>intermediate</td>
<td>2.6</td>
<td>intermediate separation</td>
</tr>
<tr>
<td>`verapamil`</td>
<td>low</td>
<td>81</td>
<td>strong hERG block offset by I\<sub\>CaL\</sub\> block — the key multichannel control</td>
</tr>
<tr>
<td>`diltiazem`</td>
<td>low</td>
<td>122</td>
<td>low-risk negative control</td>
</tr>
<tr>
<td>`control`</td>
<td>—</td>
<td>—</td>
<td>drug-free reference for boundary calibration</td>
</tr>
</table>
**IC50/Hill provenance (mandatory transcription task, Day 1):** primary source **Crumb WJ Jr, Vicente J, Johannesen L, Strauss DG.** *An evaluation of 30 clinical drugs against the proposed comprehensive in vitro proarrhythmia assay (CiPA) ion channel panel.* J Pharmacol Toxicol Methods 2016;81:251–262. doi:10.1016/j.vascn.2016.03.009 — the manual-patch multichannel IC50 set used in the CiPA in-silico papers (reproduced as Table 3 of Li et al. 2017, doi:10.1161/CIRCEP.116.004628). Free C_max values: Li et al. 2019, *Clin Pharmacol Ther* 105:466–475, doi:10.1002/cpt.1184 (CiPA training-drug table).
<callout icon="⚠️" color="red_bg">
	EVERY IC50, Hill and C_max value MUST be transcribed by a human from the cited table, entered with `source_table` and `source_doi`, marked `verification_status: VERIFIED`, and double-entered by a second team member (`transcribed_by` + reviewer field in `validation/transcription_log.md`). Until then rows stay `PLACEHOLDER` and the API returns `E_PROVENANCE_INCOMPLETE`. Do NOT let the coding model invent, recall, or interpolate pharmacology numbers. This is the single highest-risk data step in the project.
</callout>
### 5.7 Tests
`test_hill_block.py` (b=0.5 at C=IC50 for h=1; monotone in C; f∈(0,1\]; h sensitivity), `test_combination_rule.py` (multiplicative vs additive, order invariance, single-drug reduction), `test_drug_registry.py`, `test_negative_control_bad_drug_csv.py`.
---
## §6 — PK LAYER
### 6.1 Frozen decision
**No compartmental PK in v1.0. The system accepts free concentration directly.** Rationale: a one-compartment model would add three unvalidated parameters per drug (CL/F, V/F, f_u), each requiring its own provenance, without changing any conclusion of the margin/rescue layer, which operates on exposure multipliers. Adding it would violate RULE 4 and increase the number of unjustifiable numbers (RULE 12).
### 6.2 Exposure interface (frozen)
```plain text
C_free_d [nM] = exposure_multiplier_d  x  cmax_free_nM_d
exposure_multiplier_d ∈ [0, 25],  default 1.0,  UI slider on log2 scale
```
- The UI label is **"Exposure (× free C_max)"**, never "dose", never "mg".
- Alternative direct entry `c_free_nM` is permitted in the API (`exposure_mode: "absolute"`), and is converted to a multiplier for display.
- `exposure_multiplier > max_validated_multiple` → tag `OUT_OF_CALIBRATED_RANGE`, credibility ≤ `UNVERIFIED`.
### 6.3 Free-fraction handling
All registry C_max values are **free (unbound) plasma concentrations** as published. The system never converts total → free (that would require an f_u with its own provenance). Any drug whose published value is total-only is **not admissible** to the MVP set. Field `cmax_basis: free` is mandatory and asserted at load.
### 6.4 Documented limitations (must appear in the report)
No absorption/distribution/elimination, no time-varying concentration, no metabolites, no tissue partitioning, no protein-binding variability, no drug–drug PK interaction. All exposures are steady, instantaneous and declared. `test_exposure_layer.py` covers boundaries and the out-of-range tag.
---
## §7 — ELECTROLYTE / PHYSIOLOGY LAYER
### 7.1 Allowed variables (exactly three; nothing else may be settable)
<table header-row="true">
<tr>
<td>Variable</td>
<td>Model pathway</td>
<td>Valid range</td>
<td>Default</td>
<td>Hard safety bounds</td>
<td>Margin axis?</td>
<td>Rescue action?</td>
<td>Source of range</td>
</tr>
<tr>
<td>`k_o_mM` — extracellular K⁺</td>
<td>model constant `extracellular.ko`; affects I\<sub\>K1\</sub\>, I\<sub\>Kr\</sub\>, I\<sub\>Ks\</sub\> driving force and E_K</td>
<td>**2.5 – 7.0 mM**</td>
<td>**5.4 mM** (ORd baseline)</td>
<td>reject outside range; tag `OUT_OF_PHYSIOLOGICAL_RANGE` outside 3.0–5.5</td>
<td>**YES**</td>
<td>**YES** (upward correction only, to ≤ 5.4)</td>
<td>ORd 2011 baseline `ko = 5.4 mM`; clinical plausibility band 3.0–5.5 declared in `configs/domains.yaml` with rationale</td>
</tr>
<tr>
<td>`exposure_multiplier_d` — per-drug free exposure</td>
<td>Hill block → conductance scaling (§5.4)</td>
<td>0 – 25 × free C_max</td>
<td>1.0</td>
<td>\> `max_validated_multiple` → `OUT_OF_CALIBRATED_RANGE`</td>
<td>**YES** (as log₂ multiplier)</td>
<td>**YES** (reduction steps only)</td>
<td>CiPA simulations span 1–25× C_max</td>
</tr>
<tr>
<td>`cl_ms` — pacing cycle length</td>
<td>pacing protocol period</td>
<td>500 – 2000 ms</td>
<td>**2000 ms**</td>
<td>qNet/margin/rescue locked to 2000 ms</td>
<td>**NO** (D3)</td>
<td>**NO**</td>
<td>CiPA qNet protocol uses CL = 2000 ms</td>
</tr>
</table>
### 7.2 Explicitly excluded physiological variables (with reasons — display these strings)
<table header-row="true">
<tr>
<td>Variable</td>
<td>Status</td>
<td>Reason string</td>
</tr>
<tr>
<td>Mg²⁺</td>
<td>`NOT MODELLED`</td>
<td>"The selected model contains no Mg²⁺-dependent conductance or Mg²⁺ block term, and no published Mg²⁺ dose-response is calibrated for it. Including it would require inventing physiology." (D4)</td>
</tr>
<tr>
<td>Ca²⁺ extracellular</td>
<td>`NOT SETTABLE in v1.0`</td>
<td>"Changing extracellular Ca²⁺ perturbs Ca-handling calibration; out of scope for v1.0."</td>
</tr>
<tr>
<td>Na⁺ extracellular</td>
<td>`NOT SETTABLE in v1.0`</td>
<td>"No demo-relevant pathway; out of scope."</td>
</tr>
<tr>
<td>Temperature, pH, β-adrenergic tone, sex/hormonal scaling, cell-type variation</td>
<td>`NOT MODELLED in v1.0`</td>
<td>"No calibrated pathway in the selected model artefact for v1.0."</td>
</tr>
</table>
### 7.3 Tests
`test_domains.py` (range rejects, tags, defaults), `test_ko_pathway.py` (asserting that changing `k_o_mM` changes `V_rest` and qNet monotonically over 3.0–5.4 mM in the drug-free control, which is also validation Experiment 4).
---
## §8 — qNet AND THE PRIMARY INSTABILITY FUNCTIONAL Φ
### 8.1 qNet (prior art — Dutta 2017 / Li 2019)
```plain text
I_net(t) = I_NaL(t) + I_CaL(t) + I_Kr(t) + I_Ks(t) + I_K1(t) + I_to(t)      [A/F]
qNet     = ∫_{0}^{CL} I_net(t) dt                                            [C/F]
```
<table header-row="true">
<tr>
<td>Setting</td>
<td>Frozen value</td>
</tr>
<tr>
<td>Integration interval</td>
<td>the full analysis beat, `t ∈ [0, CL]`, CL = 2000 ms</td>
</tr>
<tr>
<td>Pacing</td>
<td>CL = 2000 ms, steady state per §4.4</td>
</tr>
<tr>
<td>Quadrature</td>
<td>trapezoidal rule on the uniform 0.1 ms log grid; a Simpson cross-check must agree within 0.1 % (`test_quadrature.py`)</td>
</tr>
<tr>
<td>Units</td>
<td>C/F (numerically identical to µC/µF); store SI, display µC/µF</td>
</tr>
<tr>
<td>Sign convention</td>
<td>ORd current sign convention as vendored; outward-positive net charge ⇒ control qNet is **positive** and I\<sub\>Kr\</sub\> block **decreases** qNet</td>
</tr>
<tr>
<td>Concentration scaling</td>
<td>evaluated at the requested exposure; the reference sweep 1×–4× C_max is available for the audit panel, not for Φ</td>
</tr>
</table>
### 8.2 Concentration-averaged qNet (audit only)
`qNet_avg = mean(qNet at {1,2,3,4}× C_max)` is computed only for the prior-art comparison panel, tagged `PRIOR_ART_PROTOCOL`. Φ never uses it (the margin must be a function of the *current* state, not an average over hypothetical exposures).
### 8.3 Published thresholds (reference band only — D1)
Literature-reported CiPA ordinal thresholds are approximately `threshold_1 ≈ 0.0609 µC/µF` (low vs intermediate/high) and `threshold_2 ≈ 0.0483 µC/µF` (high vs intermediate/low), derived with the **dynamic hERG binding** model and the 1–4× C_max averaging protocol (Li et al. 2019, doi:10.1002/cpt.1184; see also Dutta 2017). They are stored in `configs/thresholds.yaml` as:
```yaml
literature_reference:
  threshold_1_C_per_F: 0.0609
  threshold_2_C_per_F: 0.0483
  source_doi: "10.1002/cpt.1184"
  verification_status: PLACEHOLDER   # -> VERIFIED only after a human reads the cited paper
  comparability: LITERATURE_REFERENCE_NOT_COMPARABLE   # see Deviation D1
  usable_as_boundary: false
```
The code **must refuse** to use any threshold whose `usable_as_boundary` is false as the Φ boundary.
### 8.4 The frozen boundary definition (internal calibration)
```plain text
qNet_ctrl      = qNet( no drug, K_o = 5.4 mM, CL = 2000 ms, solver_profile = standard )
qNet_boundary  = rho * qNet_ctrl,        rho = 0.75      (configs/thresholds.yaml, default)
```
`qNet_ctrl` is computed once per (model_id, model_hash, solver_profile), cached, and printed in every report. ρ is a **declared modelling convention**, not a clinical cutoff; the UI must render the boundary as *"model-defined boundary: qNet = 75 % of drug-free control (declared convention, not a clinical threshold)"*. ρ is configurable; the report records it; changing ρ changes the `config_hash`.
### 8.5 The instability functional Φ
```plain text
Phi(x) = qNet(x) - qNet_boundary                        [C/F]

x        = modelled state (K_o, exposure multipliers), CL fixed at 2000 ms
Phi > 0  =>  SAFE SIDE of the model-defined boundary
Phi = 0  =>  ON the model-defined boundary
Phi < 0  =>  UNSAFE SIDE of the model-defined boundary
```
**Why Φ is appropriate for root finding:** qNet is an integral of continuous currents over a fixed interval of a steady-state solution; it is a smooth (C¹ in practice) function of both `K_o` and log-exposure over the declared domain, is defined even when APD90 is undefined, and does not depend on discrete event detection (unlike EAD occurrence, which is a discontinuous indicator — D2).
**Expected monotonicity (to be verified, not assumed):** qNet decreases with increasing I\<sub\>Kr\</sub\>-blocking exposure and decreases with decreasing `K_o` over 3.0–5.4 mM. Multichannel drugs (verapamil) may be non-monotone in exposure because I\<sub\>CaL\</sub\> block raises qNet while I\<sub\>Kr\</sub\> block lowers it — **this is expected and must be handled, not suppressed.**
**Non-monotonicity detection (mandatory):** on every axis, evaluate Φ on a coarse grid of `N_scan = 9` points spanning the axis box; count sign changes and sign changes of the finite-difference derivative. If `sign_changes > 1` or `derivative_sign_changes > 0`, set `PHI_MONOTONICITY = NON_MONOTONIC` on that axis, refine to `N_scan = 25`, enumerate **all** brackets, and return every root (nearest root drives the margin). A non-monotone axis may never be bisected on a single assumed bracket.
### 8.6 Repolarization-abnormality (RA) annotation — secondary only (D2)
```plain text
RA_flag components, all computed on the analysis beat:
  EAD_CANDIDATE      : exists t in (t_peak, t_end) with dV/dt > +0.01 mV/ms sustained >= 5 ms
                       while V < 0 mV and after V has fallen below V_peak - 0.3*(V_peak - V_rest)
  REPOL_FAILURE      : V(CL) > -40 mV, or no downward V_90 crossing
  MULTI_CROSSING     : more than one downward V_90 crossing
  APD90_EXTREME      : APD90 > 800 ms
RA_flag is reported with its own credibility: RA_CREDIBLE only if the tight solver profile
and the coarse/fine log-grid reproduce the same flag set; otherwise RA_STATUS = ARTEFACT_SUSPECTED.
```
RA never enters Φ, the margin, the rescue objective or the feasibility test. It may only (a) be displayed, (b) cap credibility at `UNVERIFIED` when `ARTEFACT_SUSPECTED`.
### 8.7 Language rules for Φ (enforced by a copy test)
Allowed: "model-defined repolarization-risk boundary", "crossed the model-defined boundary", "reduced margin in this model". The canonical prohibited-language list is enforced repository-wide by `test_copy_forbidden_phrases.py`; do not reproduce its entries, including as examples.
---
## §9 — MARGIN ENGINE (CORE NOVELTY, PART 1)
### 9.1 State vector and normalisation
```plain text
Raw state:         x = ( K_o [mM],  m_1, ..., m_D )        m_d = exposure multiplier of drug d
Working coords:    u = ( K_o ,  log2(m_1 + eps), ..., log2(m_D + eps) ),  eps = 1e-6
Normalised coords: z_i = (u_i - u_i^0) / s_i               (dimensionless, origin at current state x0)
Scales s:          s_K   = 1.0 mM         (one mM of K+)
                   s_m   = 1.0            (one doubling of exposure, since u is log2)
Weighting:         W = diag(w_i),  default w_i = 1 for all axes  (configs/margin.yaml)
Distance:          d_W(z) = sqrt( sum_i w_i * z_i^2 )          (weighted Euclidean, L2)
```
Units are made commensurate deliberately and the convention is displayed: **1 normalised unit = 1 mM of K⁺ = one doubling of drug exposure.** This equivalence is a declared modelling convention, printed in the UI and report; `w` is user-adjustable in the API but the default is frozen for the demo.
### 9.2 Box constraints (clinically plausible bounds)
```plain text
K_o          ∈ [3.0, 5.5] mM      (plausible band; hard model domain 2.5–7.0)
log2(m_d)    ∈ [log2(0.0625), log2(4.0)]   i.e. m_d ∈ [1/16, 4]
```
The box is part of the config and enters the hash. Points outside the box are not admissible margin directions.
### 9.3 Definition of the margin
```plain text
M  = min over z of  d_W(z)   subject to   Phi(x0 + z) = 0  and  x0 + z ∈ Box
M_signed = +M  if Phi(x0) > 0        (safe side)
         = -M  if Phi(x0) < 0        (unsafe side; distance to return to the boundary)
```
### 9.4 Algorithm (frozen, three stages)
**Stage A — axis-wise exact critical values.**<br>For each admissible axis *i*: coarse scan `N_scan = 9` (§8.5) → monotonicity classification → for every sign-changing bracket, **bisection** with `tol_z = 1e-3` normalised units, `max_iter = 20`, `max_evals_per_axis = 30`. Output per axis: `d_i` (nearest root distance, `inf` if no root in box), `critical_raw_value` (e.g. `K_o = 3.42 mM`), `all_roots`, `monotonicity`.
**Stage B — direction-sampled multi-axis minimisation.**<br>Sample unit directions in normalised space: for 2 active axes, 64 equally spaced angles; for 3, 128 Fibonacci-sphere directions; for \>3, `min(256, 64·(D−1))` quasi-random (Halton) directions with a fixed seed. Along each direction, expand radially in steps of 0.25 up to the box boundary to bracket a sign change, then bisect (`tol_z = 1e-3`, `max_iter = 15`). Take the minimum radius found.
**Stage C — local refinement.**<br>From the best Stage B point, run SciPy `minimize(method="SLSQP")` on `d_W(z)` with equality constraint `Φ = 0` and box bounds, `maxiter = 30`, finite-difference step `1e-3` in normalised units, warm-started from Stage B. Accept only if it reduces `d_W` and `|Φ| < tol_phi = 1e-4 · |qNet_ctrl|`.
**Reported result:**
```plain text
M_hat        = min(Stage A d_i, Stage B best, Stage C refined)
M_status     = EXACT_AXIS   (M_hat achieved on a single axis, bisected to tolerance)
             | SAMPLED_UB   (M_hat from direction sampling / SLSQP)
             | UNREACHABLE  (no root in Box on any axis or direction)
             | BUDGET_EXCEEDED
             | NON_MONOTONIC_HANDLED   (roots enumerated; nearest used)
M_label      = "upper bound on the true minimum weighted distance" whenever status = SAMPLED_UB
```
<callout icon="🧮" color="blue_bg">
	Honesty requirement: direction sampling gives an **upper bound** on the true minimum distance. The UI must show "≤" for `SAMPLED_UB` results and the tooltip "minimum over N sampled directions; the true minimum cannot be larger". Never call M_hat "the exact minimum distance" unless status = EXACT_AXIS with a single active axis.
</callout>
### 9.5 Budgets, caching, fallback
<table header-row="true">
<tr>
<td>Item</td>
<td>Value</td>
</tr>
<tr>
<td>Max Φ evaluations per margin call</td>
<td>300 (config `margin.max_evals`)</td>
</tr>
<tr>
<td>Per-evaluation warm start</td>
<td>nearest cached converged state (§4.6)</td>
</tr>
<tr>
<td>Evaluation cache</td>
<td>shared with L4 cache; identical states are never re-simulated</td>
</tr>
<tr>
<td>Fallback when budget exceeded</td>
<td>return Stage A axis results only, `M_status = BUDGET_EXCEEDED`, credibility ≤ `UNVERIFIED`</td>
</tr>
<tr>
<td>Fallback when any evaluation is not credible</td>
<td>margin returned with `credibility = UNVERIFIED` and `n_noncredible_evals`</td>
</tr>
</table>
### 9.6 UI phrasing (frozen; violating strings fail `test_copy_forbidden_phrases.py`)
- Headline: **"Safety margin (model-defined): 1.8 normalised units"**
- Sub-line: **"= 1.8 mM of K⁺ equivalent, or 1.8 doublings of exposure equivalent, to reach the model-defined qNet boundary."**
- Mandatory caption: **"This is a distance in modelled-state space. It is NOT a probability of clinical harm."**
- Unsafe side: **"Current state is on the unsafe side of the model-defined boundary; distance back to the boundary = 0.6 units."**
### 9.7 Tests
`test_margin_engine.py` (analytic surrogate Φ with known closed-form distance — e.g. a plane and a paraboloid in 2 axes — must be recovered within 1e-2), `test_margin_monotonicity.py` (synthetic non-monotone Φ with two roots ⇒ both reported, nearest used), `test_margin_regression.py` (golden margins for the demo scenarios), `test_margin_budget.py` (budget exhaustion path returns the documented status, never a silent number).
---
## §10 — BINDING CONSTRAINT IDENTIFICATION
### 10.1 Definition
The binding constraint is the axis whose **normalised distance to the boundary is smallest**, i.e. the variable that would reach the model-defined boundary first if moved alone from the current state. It is computed, never eyeballed.
### 10.2 Algorithm (frozen)
```plain text
Input: x0, active axes i = 1..D, Box, Phi
1. For each axis i (Stage A of §9.4, results reused from the margin call):
     d_i                = normalised distance from x0 to the nearest root along axis i (inf if none in Box)
     critical_value_i   = raw-unit value of the axis at that root (e.g. K_o = 3.42 mM)
     direction_i        = sign of the move (decrease / increase)
     reachable_i        = (d_i < inf)
2. binding_axis        = argmin_i d_i over reachable axes
3. Ties: if |d_i - d_j| <= tol_tie = 0.05 normalised units, report ALL tied axes as
   co-binding, ordered by |dPhi/dz_i| (larger sensitivity first). Never break a tie silently.
4. Local sensitivity ranking (SECONDARY, reported separately):
     g_i = dPhi/dz_i at x0 by central finite difference, h = 0.05 normalised units
     S_i = |g_i| / sum_j |g_j|                (normalised sensitivity share, %)
5. Alternative dimension = the axis with the second smallest d_i, with its critical value.
6. Output object:
     { binding_axis, d_binding, critical_value, direction, tied_axes[],
       sensitivity_share{axis: %}, alternative_axis, alternative_critical_value,
       unreachable_axes[], monotonicity{axis: MONOTONIC|NON_MONOTONIC} }
```
### 10.3 Distance vs sensitivity (must both be shown)
The two rankings answer different questions and can disagree. Frozen rule: **the binding constraint is always the distance-based winner**; the sensitivity share is displayed as "local influence" only. When the two rankings disagree, the UI must show the badge `DISTANCE != SENSITIVITY` with the tooltip: *"The most influential variable locally is not the nearest boundary; distance defines the binding constraint."*
### 10.4 Frozen output wording
```plain text
Binding constraint:        Extracellular K+
Critical boundary:         K_o = 3.42 mM   (decrease of 0.58 mM from current 4.00 mM)
Alternative dimension:     Dofetilide exposure = 1.9x free Cmax (increase of 0.93 doublings)
Unreachable in box:        Diltiazem exposure (no boundary crossing within permitted bounds)
```
### 10.5 Failure modes and tests
All axes unreachable → `binding_axis = null`, status `NO_REACHABLE_BOUNDARY_IN_BOX`, UI states that no single permitted variable reaches the boundary within the declared bounds. Non-monotone axis → nearest root used, badge shown. Tests: `test_binding_constraint.py` (analytic Φ where the answer is known by construction; tie handling; unreachable handling; disagreement badge).
---
## §11 — RESCUE ENGINE (CORE NOVELTY, PART 2)
### 11.1 Problem statement
```plain text
Given an unsafe (or insufficient-margin) state x0 with Phi(x0) < Phi_target,
find   a* = argmin_{a in A}  c(a)   subject to   Phi(x0 + Delta(a)) >= Phi_target
where A is a DECLARED FINITE action set, Delta(a) is the state change caused by a,
and c(a) is a declared intervention cost.
```
### 11.2 Target margin (frozen)
```plain text
Phi_target = tau * qNet_ctrl ,   tau = 0.05   (configs/rescue.yaml)
```
Meaning: the rescued state must sit at least 5 % of control qNet **above** the boundary, so rescue does not merely land on the boundary. `tau` is recorded in every report and enters the config hash. The UI phrase is *"target margin: qNet at least 5 % of control above the model-defined boundary"*.
### 11.3 Action space A (frozen for v1.0; single actions only)
<table header-row="true">
<tr>
<td>Action class</td>
<td>Parameterisation</td>
<td>Enumerated values</td>
<td>Permitted only if</td>
</tr>
<tr>
<td>`A0_NO_ACTION`</td>
<td>none</td>
<td>1 element (the identity action)</td>
<td>always — used as the baseline for cost comparison</td>
</tr>
<tr>
<td>`A1_K_CORRECTION`</td>
<td>target `K_o` in mM</td>
<td>`{3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4}`</td>
<td>target \> current `K_o` (upward correction only) and target ≤ 5.4</td>
</tr>
<tr>
<td>`A2_EXPOSURE_REDUCTION`</td>
<td>per drug d, multiplier factor</td>
<td>`{0.75, 0.50, 0.25}` × current multiplier</td>
<td>drug present with multiplier \> 0</td>
</tr>
<tr>
<td>`A3_DISCONTINUATION`</td>
<td>per drug d, multiplier → 0</td>
<td>1 element per drug</td>
<td>`drug_registry.discontinuable == true`</td>
</tr>
</table>
```plain text
|A| = 1 + |A1_permitted| + 3*D_present + |D_discontinuable|      (typically 1 + 7 + 6 + 1 = 15)
```
Only **single** actions are searched in v1.0 (this is what makes "no permitted single action" a meaningful and exhaustively checkable statement). Combination actions are explicitly out of scope; the response field `search_scope: "single_actions_only"` states this in every reply.
### 11.4 Cost function (frozen, declared, not clinical)
```plain text
c(A0) = 0
c(A1_K_CORRECTION to K_t)      = w_K   * (K_t - K_0) / 1.0 mM
c(A2_EXPOSURE_REDUCTION by r)  = w_E   * |log2(r)|                  (r = 0.75 -> 0.415 doublings)
c(A3_DISCONTINUATION of d)     = w_D                                (flat, dominant)
Defaults (configs/rescue.yaml): w_K = 1.0, w_E = 1.0, w_D = 6.0
```
The cost is an explicitly declared preference ordering (electrolyte correction cheapest, dose reduction next, discontinuation most costly), **not** a clinical utility. UI caption: *"Cost is a declared search preference, not a clinical judgement. Weights are configurable and printed in the report."* Ties within `tol_cost = 1e-9` are reported as co-optimal, sorted by action class then by parameter value (deterministic ordering, `test_rescue_determinism.py`).
### 11.5 Algorithm (frozen — exhaustive enumeration)
```plain text
1. Build A from the declared registry + current state. Record |A| and the enumeration order.
2. For each a in A (deterministic order):
     x_a  = apply Delta(a) to x0        (clamped to Box; if clamping changes the action, mark SKIPPED_OUT_OF_BOX)
     Evaluate Phi(x_a) via the cached EP engine (warm start allowed)
     Record: Phi(x_a), credibility(x_a), feasible = (Phi(x_a) >= Phi_target), c(a)
3. Feasible set F = { a : feasible and credibility(x_a) in {VERIFIED} }
4. If F non-empty: a* = argmin_{a in F} c(a); status = FEASIBLE
   Else: run §12 infeasibility classification.
5. Always return the FULL evaluated table (all |A| rows) so the result is auditable.
6. Also return, for the chosen action, the post-rescue margin M_hat(x_a*) (a second margin call).
```
No gradient search, no heuristics, no early exit. Every element is evaluated, which is exactly what licences the infeasibility language in §12. Budget: `|A| <= 40` enforced; if the declared set exceeds it → `E_ACTION_SET_TOO_LARGE` (a config error, never a silent truncation).
### 11.6 Excluded action classes (with reasons — display them)
<table header-row="true">
<tr>
<td>Excluded</td>
<td>Reason</td>
</tr>
<tr>
<td>Drug substitution</td>
<td>Requires indication-equivalence judgement and IC50 data for the substitute plus a therapeutic-equivalence claim we cannot justify. Out of scope for v1.0 (RULE 4, RULE 12).</td>
</tr>
<tr>
<td>Rate control / pacing change</td>
<td>qNet boundary is protocol-bound at CL = 2000 ms (D3).</td>
</tr>
<tr>
<td>Mg²⁺ administration</td>
<td>No defensible model pathway (D4).</td>
</tr>
<tr>
<td>Multi-action combinations</td>
<td>v1.0 answers the single-action question only; combinations would weaken the exhaustiveness claim without more compute budget.</td>
</tr>
<tr>
<td>Any action in clinical units (mg, mEq infused, rate)</td>
<td>Would imply dosing advice (§25).</td>
</tr>
</table>
### 11.7 Output contract
```json
{
  "status": "FEASIBLE | INFEASIBLE_EXHAUSTIVE | NO_SOLUTION_FOUND | INCOMPLETE_SEARCH",
  "search_scope": "single_actions_only",
  "phi_target": 0.0039,
  "best_action": {"class": "A1_K_CORRECTION", "param": {"k_o_mM": 4.4}, "cost": 0.4,
                   "phi_after": 0.0051, "margin_after": 1.12, "credibility": "VERIFIED"},
  "co_optimal": [],
  "evaluated": [ {"action": "...", "cost": 0.0, "phi": -0.0021, "feasible": false,
                   "credibility": "VERIFIED"} ],
  "action_set_size": 15,
  "n_noncredible": 0,
  "disclaimer": "DISC_RESCUE"
}
```
### 11.8 Tests
`test_rescue_engine.py` (feasible case, correct minimum cost, deterministic tie order), `test_rescue_exhaustive.py` (asserts every action in A was evaluated — count check against `|A|`), `test_rescue_post_margin.py` (post-rescue margin ≥ target), `test_rescue_determinism.py`, `test_rescue_out_of_box.py`.
---
## §12 — INFEASIBILITY CERTIFICATE (LANGUAGE DISCIPLINE IS MANDATORY)
### 12.1 What can and cannot be proved
The rescue search is an **exhaustive enumeration of a finite, declared set** `A`. Therefore the following statement is a genuine, complete result *about that set*:
> For every a ∈ A, the deterministic simulator returned Φ(x₀ + Δ(a)) \< Φ_target, and every one of those evaluations passed the credibility gate. Hence no element of A restores the target margin.
This is **exhaustive finite-domain infeasibility**. It is complete with respect to `A`, the simulator, and the declared tolerances. It is **not** a mathematical proof about physiology, about actions outside `A`, about combinations of actions, or about continuous action values between the enumerated grid points. It carries the numerical caveat that each Φ evaluation has finite solver tolerance; margins within `tol_phi` of `Φ_target` are reported as `BORDERLINE` and force the weaker status (see 12.2).
### 12.2 Status taxonomy (frozen — exactly four states)
<table header-row="true">
<tr>
<td>Status</td>
<td>Precondition</td>
<td>Permitted user-facing wording</td>
</tr>
<tr>
<td>`FEASIBLE`</td>
<td>≥ 1 credible feasible action</td>
<td>"Minimum-cost permitted single action found."</td>
</tr>
<tr>
<td>`INFEASIBLE_EXHAUSTIVE`</td>
<td>all `|A|` actions evaluated; **all** credibility `VERIFIED`; all `Φ < Φ_target − tol_phi`</td>
<td>**"Certificate of infeasibility over the declared finite action set: no permitted single action restores the target margin."** (must be followed by `DISC_INFEAS`)</td>
</tr>
<tr>
<td>`NO_SOLUTION_FOUND`</td>
<td>all actions evaluated, but ≥ 1 result is `BORDERLINE` (within `tol_phi` of the target) while none is clearly feasible</td>
<td>"No feasible single intervention found within the defined search domain (one or more results are within numerical tolerance of the target)."</td>
</tr>
<tr>
<td>`INCOMPLETE_SEARCH`</td>
<td>≥ 1 action evaluation failed, timed out, was `UNVERIFIED`/`FAILED`, or was skipped out-of-box</td>
<td>"Search incomplete — feasibility unknown. N of M actions could not be credibly evaluated."</td>
</tr>
</table>
Restricted wording for anything except `INFEASIBLE_EXHAUSTIVE` is enforced by `test_infeasibility_language.py`. Separately, the repository-wide copy test enforces the canonical prohibited-language list; do not reproduce those entries in documentation.
### 12.3 Mandatory explanation payload
When the status is `INFEASIBLE_EXHAUSTIVE` or `NO_SOLUTION_FOUND`, the engine must return the computational reason:
```json
{
  "reason_code": "K_CEILING_BINDING",
  "explanation": "The largest permitted K+ correction (to 5.4 mM) raises Phi to -0.0008 C/F, still below the target 0.0039 C/F. The largest permitted single exposure reduction (0.25x on dofetilide) raises Phi to 0.0012 C/F, also below target. Discontinuation is not permitted for either drug in the registry.",
  "closest_action": {"class": "A2_EXPOSURE_REDUCTION", "param": {"drug": "dofetilide", "factor": 0.25},
                     "phi": 0.0012, "shortfall": 0.0027},
  "shortfall_normalised": 0.69,
  "limiting_bound": "A1 ceiling K_o <= 5.4 mM; A2 floor factor >= 0.25; A3 not permitted",
  "what_would_help": "Two-action combinations and drug substitution are outside the declared search scope."
}
```
Reason codes (frozen enum): `K_CEILING_BINDING`, `EXPOSURE_FLOOR_BINDING`, `DISCONTINUATION_NOT_PERMITTED`, `MULTIPLE_BOUNDS_BINDING`, `TARGET_TOO_STRICT`, `NON_CREDIBLE_EVALUATIONS`.
### 12.4 Tests
`test_infeasibility_certificate.py` — constructs a scenario (Experiment 8, §16) where the finite set provably cannot reach the target with an analytic surrogate Φ, and asserts: status is `INFEASIBLE_EXHAUSTIVE`, `evaluated` has exactly `|A|` rows, `closest_action` and `shortfall` are correct, and the emitted wording matches the frozen mapping. A companion test injects one `UNVERIFIED` evaluation and asserts the status **downgrades** to `INCOMPLETE_SEARCH`.
---
## §13 — BLIND-SPOT AUDITOR (SUPPORTING LAYER S2)
### 13.1 Purpose
Quantify, for a declared sweep of one modelled variable, the interval over which a categorical/ordinal clinical score is **constant** while Φ (and the margin) change materially. The claim is about *sensitivity*, never about correctness.
### 13.2 Tisdale score implementation (prior art — Tisdale JE et al., Circ Cardiovasc Qual Outcomes 2013;6:479–487, doi:10.1161/CIRCOUTCOMES.113.000152)
The risk-score items and points are transcribed from the cited paper into `data/scores/tisdale.yaml` with `source_doi`, `source_table` and `verification_status`, exactly like drug parameters (§5.6 discipline applies). The loader refuses `PLACEHOLDER` rows. Frozen structure:
```yaml
score_id: tisdale_2013
source_doi: "10.1161/CIRCOUTCOMES.113.000152"
verification_status: PLACEHOLDER     # human must transcribe items and points from the paper
items:
  - id: age_ge_68
    type: boolean
    points: <TRANSCRIBE>
  - id: female_sex
    type: boolean
    points: <TRANSCRIBE>
  - id: loop_diuretic
    type: boolean
    points: <TRANSCRIBE>
  - id: serum_k_le_3_5
    type: threshold
    variable: k_o_mM          # the ONLY item coupled to a modelled variable
    operator: "<="
    threshold: 3.5
    points: <TRANSCRIBE>
  - id: admission_qtc_ge_450
    type: boolean
    points: <TRANSCRIBE>
  - id: acute_mi
    type: boolean
    points: <TRANSCRIBE>
  - id: qt_prolonging_drugs_count
    type: categorical         # 1 drug vs >=2 drugs
    points_map: {one: <TRANSCRIBE>, two_or_more: <TRANSCRIBE>}
  - id: sepsis
    type: boolean
    points: <TRANSCRIBE>
  - id: heart_failure
    type: boolean
    points: <TRANSCRIBE>
bands:
  - {label: low, max_inclusive: <TRANSCRIBE>}
  - {label: moderate, max_inclusive: <TRANSCRIBE>}
  - {label: high, min_inclusive: <TRANSCRIBE>}
```
**Critical modelling honesty note (must be displayed):** the score item uses **serum potassium**, while the model variable is **extracellular potassium at the myocyte**. These are related but not identical quantities. The auditor maps `serum_K := k_o_mM` as a **declared 1:1 proxy assumption** (`ASSUMPTION_SERUM_KO_PROXY_v1`) and states it in the panel. Any scenario field not supplied by the declared scenario YAML (sex, age, diuretic, sepsis, HF, MI, admission QTc) is scored `UNKNOWN`, and the score is reported as an **interval** `[score_min, score_max]` over the unknown items — never as a fake point value (D5, RULE 12).
### 13.3 Methodology (frozen)
```plain text
Input: base scenario, sweep variable v (K_o or one exposure), sweep grid G (N = 21 points),
       declared non-modelled score inputs (may be UNKNOWN)
For each g in G:
    Phi_g       = Phi(state with v = g)            (cached EP evaluations)
    M_g         = signed margin (Stage A only, for speed; flag METHOD = AXIS_ONLY)
    S_g         = Tisdale score interval [min, max] and band(s)
Outputs:
    curve_phi[G], curve_margin[G], curve_score[G]
    insensitivity_intervals = maximal contiguous sub-intervals of G where
        band(S_g) is constant AND |Phi(g) - Phi(g_start)| >= delta_phi_min
        with delta_phi_min = 0.02 * qNet_ctrl                    (declared)
    crossing_point = first g where Phi changes sign (if any)
    score_at_crossing = S_g at that point
    verdict_string (see 13.4)
```
### 13.4 Frozen verdict wording
> "Over K⁺ = 4.5 → 3.6 mM the Tisdale band remains **moderate** (score interval unchanged at \[x, y\]) because its potassium item is a threshold at ≤ 3.5 mM, while the mechanistic margin in this model falls from +2.3 to −0.4 normalised units and crosses the model-defined boundary at K⁺ = 3.9 mM. The score is **insensitive to this modelled variable over this interval**; this comparison does not establish that the score is incorrect."
The canonical prohibited-language list includes overclaims about score comparison and is enforced by the copy test; do not reproduce its entries here.
### 13.5 CredibleMeds handling (licensing)
CredibleMeds QT-risk lists are **not redistributed**. `drug_registry.yaml` has an optional `qt_risk_class_manual` field a user may fill in locally, with attribution text "Class per CredibleMeds (accessed locally by user; not distributed with this software)". No CredibleMeds file, scrape, or cached copy may enter the repository (`test_no_redistributed_licensed_data.py` scans `data/` for a forbidden-file manifest). If the field is null, the UI shows `CLASS NOT ENTERED`.
### 13.6 Tests
`test_tisdale_scoring.py` (item points, band boundaries, UNKNOWN interval logic, threshold behaviour exactly at 3.5), `test_blindspot_auditor.py` (synthetic Φ curve + synthetic score ⇒ known insensitivity interval), `test_no_redistributed_licensed_data.py`.
---
## §14 — VERIFICATION / CREDIBILITY ENGINE (SUPPORTING LAYER S3)
### 14.1 Two tiers
<table header-row="true">
<tr>
<td>Tier</td>
<td>When it runs</td>
<td>Cost</td>
<td>Feeds</td>
</tr>
<tr>
<td>**Per-request gates (fast)**</td>
<td>inside every simulate/margin/rescue call</td>
<td>\< 100 ms overhead</td>
<td>the result's own credibility</td>
</tr>
<tr>
<td>**Offline battery (heavy)**</td>
<td>`scripts/run_verification.py`, keyed by `config_hash`; results stored in `validation/battery_results/<config_hash>.json`</td>
<td>minutes</td>
<td>credibility of every request sharing that config hash</td>
</tr>
</table>
A request whose `config_hash` has **no** battery record is `UNVERIFIED` — never `VERIFIED` (A3, RULE 11).
### 14.2 Check register (frozen IDs)
<table header-row="true">
<tr>
<td>ID</td>
<td>Check</td>
<td>Tier</td>
<td>Pass criterion</td>
<td>Mandatory for VERIFIED</td>
</tr>
<tr>
<td>V-1</td>
<td>Model integrity</td>
<td>request</td>
<td>`.mmt` SHA-256 matches `CHECKSUMS.txt`; all label bindings present</td>
<td>YES</td>
</tr>
<tr>
<td>V-2</td>
<td>Steady-state convergence</td>
<td>request</td>
<td>C1–C4 of §4.4 satisfied</td>
<td>YES</td>
</tr>
<tr>
<td>V-3</td>
<td>Unit & range checks</td>
<td>request</td>
<td>all inputs within declared domains; no `NaN`/`inf` in trace; `V_peak > 0`; `V_rest ∈ [−95, −75]` mV drug-free</td>
<td>YES</td>
</tr>
<tr>
<td>V-4</td>
<td>Quadrature consistency</td>
<td>request</td>
<td>trapezoid vs Simpson qNet agree within 0.1 %</td>
<td>YES</td>
</tr>
<tr>
<td>V-5</td>
<td>Provenance completeness</td>
<td>request</td>
<td>every used parameter has `source_doi`  • `verification_status = VERIFIED`</td>
<td>YES</td>
</tr>
<tr>
<td>V-6</td>
<td>Baseline APD90 reproduction</td>
<td>battery</td>
<td>drug-free APD90 within ±5 ms of `validation/reference_values.yaml: apd90_control_ms` (recorded from the primary reference implementation and cross-checked against the source publication; stays `UNKNOWN` until a human records it)</td>
<td>YES</td>
</tr>
<tr>
<td>V-7</td>
<td>Baseline qNet reproduction</td>
<td>battery</td>
<td>drug-free qNet within ±2 % of recorded `qnet_control_C_per_F`</td>
<td>YES</td>
</tr>
<tr>
<td>V-8</td>
<td>Tolerance/timestep sensitivity</td>
<td>battery</td>
<td>`standard` vs `tight` profile: `|ΔqNet|/qNet < 1 %` and `|ΔAPD90| < 1 ms`; `dt_log` 0.1 vs 0.02 ms: `|ΔqNet|/qNet < 0.2 %`</td>
<td>YES</td>
</tr>
<tr>
<td>V-9</td>
<td>Independent solver cross-check</td>
<td>battery</td>
<td>Myokit/CVODES vs SciPy `BDF` on the Myokit-exported Python RHS (`models/generated/ord_rhs.py`): `|ΔAPD90| < 2 ms`, `|ΔqNet|/qNet < 2 %` on the control and one drug case</td>
<td>YES</td>
</tr>
<tr>
<td>V-10</td>
<td>Warm-start equivalence</td>
<td>battery</td>
<td>§4.6 gate</td>
<td>YES (else warm start disabled)</td>
</tr>
<tr>
<td>V-11</td>
<td>Known-drug direction</td>
<td>battery</td>
<td>dofetilide 1× C_max: qNet decreases and APD90 increases vs control (both beyond V-8 noise)</td>
<td>YES</td>
</tr>
<tr>
<td>V-12</td>
<td>Prior-art ordering sanity</td>
<td>battery</td>
<td>at 1× C_max, `qNet(dofetilide) < qNet(cisapride) < qNet(diltiazem)` and `qNet(dofetilide) < qNet(verapamil)`</td>
<td>YES</td>
</tr>
<tr>
<td>V-13</td>
<td>K⁺ directionality</td>
<td>battery</td>
<td>qNet is monotonically non-increasing as `K_o` falls 5.4 → 3.0 mM, drug-free</td>
<td>YES</td>
</tr>
<tr>
<td>V-14</td>
<td>Stimulus sensitivity</td>
<td>battery</td>
<td>±20 % stimulus amplitude changes qNet by \< 1 % and APD90 by \< 2 ms</td>
<td>NO (advisory; failure caps at `UNVERIFIED`)</td>
</tr>
<tr>
<td>V-15</td>
<td>RA reproducibility</td>
<td>battery</td>
<td>RA flag set identical under `standard` and `tight` profiles for the demo scenarios</td>
<td>NO (governs `RA_STATUS` only)</td>
</tr>
<tr>
<td>V-16</td>
<td>Negative controls behave</td>
<td>battery</td>
<td>every §17 negative control produces `FAILED` or `UNVERIFIED`, never `VERIFIED`</td>
<td>YES (a battery that cannot fail is not a battery)</td>
</tr>
</table>
### 14.3 Per-check states and aggregation (frozen)
```plain text
Each check -> PASS | FAIL | UNKNOWN

credibility(result):
  FAILED      if any mandatory check == FAIL
  UNVERIFIED  if no mandatory FAIL, but any mandatory check == UNKNOWN
              or the result carries OUT_OF_CALIBRATED_RANGE / OUT_OF_PHYSIOLOGICAL_RANGE
              or COMBO_RULE_SENSITIVE / partial_panel / RA ARTEFACT_SUSPECTED
              or M_status in {BUDGET_EXCEEDED}
  VERIFIED    only if ALL mandatory checks == PASS and no downgrade tag is present
```
`UNKNOWN` is never coerced to `PASS`. Aggregate results always carry the **worst** state of their inputs: a margin built from any non-`VERIFIED` Φ evaluation cannot be `VERIFIED`, and a rescue result cannot be `VERIFIED` if any evaluated action was not.
### 14.4 Display rules (RULE 11)
<table header-row="true">
<tr>
<td>State</td>
<td>UI treatment</td>
</tr>
<tr>
<td>`VERIFIED`</td>
<td>normal rendering + "Verified" chip listing the passed mandatory checks and the battery `config_hash`</td>
</tr>
<tr>
<td>`UNVERIFIED`</td>
<td>amber banner `DISC_UNVERIFIED`, numbers rendered in a muted/struck style, margin and rescue values shown but marked "not trustworthy — debug only", export watermarked `UNVERIFIED`</td>
</tr>
<tr>
<td>`FAILED`</td>
<td>red banner, **numeric results hidden behind an explicit "show anyway (debug)" toggle**, no green/red safety verdict of any kind, export watermarked `FAILED`</td>
</tr>
</table>
A failed or unknown verification never yields a clinical-looking verdict. There is no code path in which a hidden default turns `UNKNOWN` into a pass.
### 14.5 Tests
`test_verification_engine.py` (aggregation truth table, all 3\^n-relevant combinations for mandatory/advisory mixes), `test_verification_missing_battery.py` (no battery record ⇒ `UNVERIFIED`), `test_negative_controls.py` (§17), `test_display_rules.py` (frontend contract test asserting banner/watermark per state).
---
## §15 — VALIDATION DATASET AND REFERENCE MATERIALS
### 15.1 Source register (all public, no credentialing, no PHI)
<table header-row="true">
<tr>
<td>Source</td>
<td>Purpose</td>
<td>Exact information used</td>
<td>Access / licence concerns</td>
<td>Local storage</td>
</tr>
<tr>
<td>Physiome Model Repository exposure `models.cellml.org/e/5a0` — `ohara_rudy_cipa_v1_2017.cellml`</td>
<td>primary model artefact</td>
<td>full CellML model</td>
<td>public, freely downloadable; record licence text as published</td>
<td>`models/vendor/*.cellml`  • `PROVENANCE.yaml`</td>
</tr>
<tr>
<td>`github.com/FDA/CiPA` (GPL-3.0)</td>
<td>independent numerical reference (V-9 context) and protocol reference</td>
<td>`AP_simulation/models/newordherg_qNet.c` read **for reference only**</td>
<td>GPL-3.0 — **do not copy code into this repository**; cite and compare numbers only</td>
<td>not vendored; URL + commit hash recorded in `docs/REFERENCES.md`</td>
</tr>
<tr>
<td>O'Hara 2011, PLoS Comput Biol 7(5):e1002061</td>
<td>physiology provenance, control APD90 reference</td>
<td>published control APD90 / AP morphology figures</td>
<td>open access</td>
<td>`docs/REFERENCES.md`</td>
</tr>
<tr>
<td>Dutta 2017, Front Physiol 8:616</td>
<td>conductance scaling, qNet definition, protocol</td>
<td>scaling factors table; qNet definition; CL = 2000 ms protocol</td>
<td>open access</td>
<td>`docs/REFERENCES.md`  • `configs/model.yaml`</td>
</tr>
<tr>
<td>Li 2019, Clin Pharmacol Ther 105:466–475</td>
<td>qNet threshold reference band; CiPA free C_max table; risk labels</td>
<td>threshold values (reference only, D1); free C_max; prior-art risk labels</td>
<td>open access / publisher terms; store values, not PDFs</td>
<td>`configs/thresholds.yaml`, `data/drug_registry.yaml`</td>
</tr>
<tr>
<td>Crumb 2016, J Pharmacol Toxicol Methods 81:251–262</td>
<td>multichannel IC50 / Hill parameters</td>
<td>per-drug per-channel IC50 and Hill values for the 6 MVP drugs</td>
<td>publisher terms; store transcribed numeric values with citation, no PDF in repo</td>
<td>`data/drug_parameters.csv`</td>
</tr>
<tr>
<td>Tisdale 2013, Circ Cardiovasc Qual Outcomes 6:479–487</td>
<td>clinical score for the blind-spot audit</td>
<td>score items, points, band cut-offs</td>
<td>open access</td>
<td>`data/scores/tisdale.yaml`</td>
</tr>
<tr>
<td>CredibleMeds</td>
<td>optional risk-class annotation</td>
<td>nothing stored</td>
<td>**licensed — not redistributable**; user-entered field only (§13.5)</td>
<td>none</td>
</tr>
</table>
No dataset containing patient data of any kind is used anywhere in this project (RULE 16).
### 15.2 `data/drug_parameters.csv` — schema and example row
Schema as §5.2. Example (values shown as `PLACEHOLDER` deliberately — the human transcriber replaces them):
```javascript
drug_id,drug_name,channel,ic50_nM,hill,ic50_ci_low_nM,ic50_ci_high_nM,n_replicates,assay,temperature_C,source_citation,source_doi,source_table,units_check,na_reason,verification_status,transcribed_by,transcribed_on
dofetilide,Dofetilide,IKr,PLACEHOLDER,PLACEHOLDER,,,,manual patch clamp,37,"Crumb et al. 2016 J Pharmacol Toxicol Methods 81:251-262",10.1016/j.vascn.2016.03.009,"Table 2",IKr_pIC50_nM|hill_dimensionless,,PLACEHOLDER,,
dofetilide,Dofetilide,ICaL,PLACEHOLDER,PLACEHOLDER,,,,manual patch clamp,37,"Crumb et al. 2016",10.1016/j.vascn.2016.03.009,"Table 2",IKr_pIC50_nM|hill_dimensionless,,PLACEHOLDER,,
verapamil,Verapamil,IKr,PLACEHOLDER,PLACEHOLDER,,,,manual patch clamp,37,"Crumb et al. 2016",10.1016/j.vascn.2016.03.009,"Table 2",IKr_pIC50_nM|hill_dimensionless,,PLACEHOLDER,,
```
### 15.3 `validation/validation_cases.yaml` — schema
```yaml
schema_version: 1
cases:
  - case_id: VC-001-control-apd90
    experiment: E1
    description: "Drug-free control, K_o = 5.4 mM, CL = 2000 ms, endo"
    state:
      drugs: []
      k_o_mM: 5.4
      cl_ms: 2000
      cell_type: endo
      solver_profile: standard
    expected:
      metric: apd90_ms
      reference_value: UNKNOWN        # human records from reference implementation + publication
      reference_source_doi: "10.3389/fphys.2017.00616"
      tolerance: {type: absolute, value: 5.0}
    pass_criterion: "|computed - reference| <= tolerance"
    on_fail: "Block VERIFIED status for this config_hash (V-6)"
  - case_id: VC-010-dofetilide-direction
    experiment: E2
    description: "Dofetilide 1x free Cmax lowers qNet and prolongs APD90 vs control"
    state: {drugs: [{id: dofetilide, exposure_multiplier: 1.0], k_o_mM: 5.4, cl_ms: 2000,
            cell_type: endo, solver_profile: standard}
    expected:
      metric: relational
      assertion: "qNet < qNet_control - 3*noise_qNet AND apd90 > apd90_control + 2.0"
    pass_criterion: "assertion true"
    on_fail: "V-11 FAIL -> credibility FAILED for this config"
```
`validation/reference_values.yaml` holds the recorded reference numbers, each with `value`, `status: UNKNOWN|RECORDED`, `recorded_by`, `recorded_on`, `source_doi`, `method` ("read from publication" / "computed with reference implementation"). Any reference still `UNKNOWN` makes its check `UNKNOWN`, not `PASS` (RULE 12).
### 15.4 Storage rules
All validation artefacts are plain text in-repo (`csv`, `yaml`, `json`), no binaries except the vendored CellML/mmt, no PDFs of papers, no licensed content. `scripts/verify_data_integrity.py` checks: every parameter row has a DOI; no file listed in `data/FORBIDDEN_MANIFEST.txt` exists; all `verification_status` values are legal.
---
## §16 — VALIDATION EXPERIMENTS
All experiments are executed by `scripts/run_verification.py` and reported in `validation/battery_results/<config_hash>.json` plus a human-readable `validation/REPORT.md`.
<table header-row="true">
<tr>
<td>ID</td>
<td>Hypothesis</td>
<td>Input</td>
<td>Output</td>
<td>Pass criterion</td>
<td>Failure interpretation</td>
</tr>
<tr>
<td>**E1 — Control reproduction**</td>
<td>The vendored model, run with our solver and protocol, reproduces the published/reference control behaviour</td>
<td>drug-free, `K_o` 5.4, CL 2000, endo, `standard`</td>
<td>APD90, qNet, `V_rest`, `V_peak`, `dVdt_max`</td>
<td>APD90 within ±5 ms and qNet within ±2 % of `reference_values.yaml`</td>
<td>Our harness (protocol, stimulus, steady state or biomarker code) is wrong — **not** the model. Block all `VERIFIED` status until resolved.</td>
</tr>
<tr>
<td>**E2 — Known drug response**</td>
<td>A selective I\<sub\>Kr\</sub\> blocker lowers qNet and prolongs APD90</td>
<td>dofetilide at 0.5×, 1×, 2×, 4× C_max</td>
<td>qNet, APD90 curves</td>
<td>monotone qNet decrease and APD90 increase across the series, beyond V-8 numerical noise</td>
<td>Block application, IC50 transcription, or channel-to-conductance mapping is wrong</td>
</tr>
<tr>
<td>**E3 — Prior-art ordering**</td>
<td>Our Hill-block pipeline preserves the qualitative CiPA-label ordering</td>
<td>all 6 drugs at 1× and 4× C_max</td>
<td>qNet table + rank list</td>
<td>`qNet(dofetilide) < qNet(cisapride) < qNet(diltiazem)`; `qNet(dofetilide) < qNet(verapamil)`; rank correlation with CiPA labels ≥ 0</td>
<td>Multichannel data or the combination/scaling path is wrong. **Note (D1):** exact numerical agreement with published CiPA qNet is *not* expected and its absence is not a failure.</td>
</tr>
<tr>
<td>**E4 — K⁺ directionality**</td>
<td>Falling `K_o` reduces qNet</td>
<td>drug-free sweep `K_o` = 5.4 → 3.0 mM, 13 points</td>
<td>qNet, APD90, `V_rest` curves</td>
<td>qNet monotonically non-increasing; `V_rest` becomes more negative as `K_o` falls; no `NaN`</td>
<td>The electrolyte pathway is mis-wired (wrong constant set), which would invalidate the entire demo</td>
</tr>
<tr>
<td>**E5 — Numerical sensitivity**</td>
<td>Results are insensitive to solver settings within declared tolerances</td>
<td>E1 and E2 cases under `standard`, `tight`, `coarse_log`; and under `loose_NEGATIVE_CONTROL`</td>
<td>deltas per V-8</td>
<td>V-8 thresholds met for `standard` vs `tight`; `loose_NEGATIVE_CONTROL` must **fail**</td>
<td>If `standard` fails, tighten defaults and re-baseline. If the loose control passes, the battery is not discriminating (bug in the gate)</td>
</tr>
<tr>
<td>**E6 — Margin consistency**</td>
<td>The margin engine's distance is self-consistent and correct on known geometry</td>
<td>(a) analytic surrogate Φ (plane, paraboloid) (b) real Φ, single-axis case</td>
<td>`M_hat`, `M_status`, axis roots</td>
<td>(a) analytic distance recovered within 1e-2 (b) `Φ(x0 + M_hat·n̂) = 0` within `tol_phi`; bisection reproducible; `M_hat` decreases monotonically as the state approaches the boundary along a monotone axis</td>
<td>Root-finding, normalisation or weighting is wrong; margin must not be displayed</td>
</tr>
<tr>
<td>**E7 — Rescue consistency**</td>
<td>The reported action truly restores the target margin, and it is the cheapest that does</td>
<td>demo unsafe state</td>
<td>rescue table</td>
<td>`Φ(x0 + Δ(a*)) ≥ Φ_target` recomputed independently; no cheaper feasible action exists in the evaluated table; all `|A|` rows present</td>
<td>Enumeration, cost ordering or feasibility comparison is wrong</td>
</tr>
<tr>
<td>**E8 — Infeasibility behaviour**</td>
<td>On a state where the finite action set demonstrably cannot reach the target, the engine returns exhaustive infeasibility with the correct reason</td>
<td>severe scenario (e.g. dofetilide 4× + `K_o` 3.0 with `discontinuable: false` and `A1` ceiling 5.4)</td>
<td>status, reason code, closest action, shortfall</td>
<td>status `INFEASIBLE_EXHAUSTIVE` with `|evaluated| = |A|`, correct `reason_code`, correct `closest_action`; and when one evaluation is force-marked `UNVERIFIED` the status downgrades to `INCOMPLETE_SEARCH`</td>
<td>Language/status discipline is broken — the most reputationally dangerous failure in the project</td>
</tr>
<tr>
<td>**E9 — Clinical-score blind spot**</td>
<td>Over a declared K⁺ interval the Tisdale band is constant while the mechanistic margin crosses the boundary</td>
<td>demo scenario, `K_o` sweep 5.0 → 3.6 mM, declared score inputs</td>
<td>score curve, Φ curve, insensitivity intervals, crossing point</td>
<td>≥ 1 insensitivity interval detected with `|ΔΦ| ≥ 0.02·qNet_ctrl` and constant band; wording matches §13.4</td>
<td>Either the sweep is uninteresting (choose declared inputs so the score band is genuinely constant) or the auditor logic is wrong. **Never** tune the score to manufacture a blind spot — the score items are transcribed and immutable</td>
</tr>
</table>
Every experiment records: inputs, outputs, `config_hash`, `result_hash`, timestamp, code version, and `PASS/FAIL/UNKNOWN`.
---
## §17 — NEGATIVE CONTROLS (THE BATTERY MUST BE ABLE TO FAIL)
<table header-row="true">
<tr>
<td>ID</td>
<td>Deliberate defect</td>
<td>Expected system response</td>
<td>Test</td>
</tr>
<tr>
<td>N-1</td>
<td>`solver_profile = loose_NEGATIVE_CONTROL` (rtol 1e-4, atol 1e-6, max step 5 ms)</td>
<td>V-8 FAIL → credibility `FAILED`; UI red banner; results hidden behind debug toggle</td>
<td>`test_negative_controls.py::test_loose_solver`</td>
</tr>
<tr>
<td>N-2</td>
<td>Insufficient pacing: `n_prepace = 5`, convergence checks enabled</td>
<td>V-2 FAIL (`E_NO_STEADY_STATE`) → `FAILED`; no margin emitted</td>
<td>`::test_insufficient_pacing`</td>
</tr>
<tr>
<td>N-3</td>
<td>Out-of-domain exposure: 200× C_max</td>
<td>`E_DOMAIN_EXPOSURE` reject at L1; if forced via config, `OUT_OF_CALIBRATED_RANGE` → `UNVERIFIED`</td>
<td>`::test_out_of_domain_exposure`</td>
</tr>
<tr>
<td>N-4</td>
<td>Malformed drug data: negative IC50, Hill = 0, missing DOI, wrong units string</td>
<td>loader abort `E_PROVENANCE_INCOMPLETE` / `E_UNITS`; server refuses to start with that data file</td>
<td>`test_negative_control_bad_drug_csv.py`</td>
</tr>
<tr>
<td>N-5</td>
<td>Corrupted model file (one byte changed in `.mmt`)</td>
<td>`E_MODEL_HASH_MISMATCH` at startup</td>
<td>`::test_model_hash_mismatch`</td>
</tr>
<tr>
<td>N-6</td>
<td>Reference values left `UNKNOWN`</td>
<td>V-6/V-7 `UNKNOWN` → credibility `UNVERIFIED`, never `VERIFIED`</td>
<td>`test_verification_missing_battery.py`</td>
</tr>
<tr>
<td>N-7</td>
<td>Injected non-credible action evaluation in a rescue search</td>
<td>status downgrades `INFEASIBLE_EXHAUSTIVE` → `INCOMPLETE_SEARCH`</td>
<td>`test_infeasibility_certificate.py::test_downgrade`</td>
</tr>
<tr>
<td>N-8</td>
<td>Synthetic "EAD" produced only under `loose` settings</td>
<td>RA `ARTEFACT_SUSPECTED`; not displayed as a verified abnormality</td>
<td>`::test_ead_artefact_rejected`</td>
</tr>
<tr>
<td>N-9</td>
<td>Non-monotone synthetic Φ with two roots</td>
<td>`NON_MONOTONIC` flagged, all roots reported, nearest used, no silent single-bracket bisection</td>
<td>`test_margin_monotonicity.py`</td>
</tr>
</table>
The negative-control suite is part of CI. If any negative control silently passes, the build fails (V-16). This is presented in the demo as a **feature**: the system can detect its own numerical failure.
---
## §18 — DATA AND PROVENANCE
### 18.1 Citation format (frozen)
```json
{"id": "crumb2016",
 "authors": "Crumb WJ Jr, Vicente J, Johannesen L, Strauss DG",
 "year": 2016,
 "title": "An evaluation of 30 clinical drugs against the proposed CiPA ion channel panel",
 "venue": "J Pharmacol Toxicol Methods 81:251-262",
 "doi": "10.1016/j.vascn.2016.03.009",
 "used_for": ["IC50", "hill"],
 "accessed_on": "YYYY-MM-DD"}
```
All citations live in `docs/REFERENCES.json` (machine-readable) and are rendered into `docs/REFERENCES.md`. Every parameter row references a citation `id`; `scripts/verify_data_integrity.py` fails if an `id` is missing from the register.
### 18.2 Provenance record attached to every result (frozen fields)
```json
{
  "software": {"name": "TorsadeTwin", "version": "0.1.0", "git_commit": "<sha>", "built_on": "<iso>"},
  "model": {"model_id": "ORd-CiPA-v1.0", "artefact": "models/ord_cipa_v1.mmt",
            "artefact_sha256": "<sha>", "source_url": "https://models.cellml.org/e/5a0",
            "source_retrieved_on": "<date>", "citations": ["ohara2011", "dutta2017", "li2017"],
            "herg_dynamic_binding": "DISABLED (deviation D1)"},
  "solver": {"engine": "myokit.Simulation/CVODES", "myokit_version": "<v>", "sundials_version": "<v>",
             "profile": "standard", "rtol": 1e-8, "atol": 1e-10, "max_step_ms": 1.0,
             "python": "<v>", "numpy": "<v>", "scipy": "<v>", "platform": "<os/arch>"},
  "protocol": {"cl_ms": 2000, "n_prepace": 1000, "stimulus": {"amp_A_per_F": -80, "dur_ms": 0.5},
               "dt_log_ms": 0.1, "cell_type": "endo"},
  "parameters": [{"drug_id": "dofetilide", "channel": "IKr", "ic50_nM": 0.0, "hill": 0.0,
                  "citation": "crumb2016", "source_table": "Table 2",
                  "verification_status": "VERIFIED"}],
  "assumptions": ["COMBO_RULE_INDEP_MULT_v1", "ASSUMPTION_SERUM_KO_PROXY_v1",
                  "BOUNDARY_RHO_0.75_DECLARED_CONVENTION"],
  "boundary": {"qnet_ctrl_C_per_F": 0.0, "rho": 0.75, "qnet_boundary_C_per_F": 0.0,
               "literature_reference": "LITERATURE_REFERENCE_NOT_COMPARABLE"},
  "config_hash": "<sha256>",
  "result_hash": "<sha256>",
  "credibility": {"state": "VERIFIED", "checks": {"V-1": "PASS", "V-6": "PASS"},
                  "battery_config_hash": "<sha256>", "battery_run_on": "<iso>"},
  "timestamp_utc": "<iso>",
  "disclaimers": ["DISC_GLOBAL", "DISC_MARGIN"]
}
```
### 18.3 Hashing rules (frozen)
```plain text
config_hash = sha256( canonical_json( model block + solver block + protocol block
                                      + thresholds + margin config + rescue config
                                      + drug parameter table digest ) )
input_hash  = sha256( canonical_json( StateSpec ) )
result_hash = sha256( config_hash + input_hash + canonical_json(numeric outputs, %.12e) )
```
`canonical_json`: UTF-8, sorted keys, no whitespace, floats formatted `%.12e`, no timestamps inside hashed payloads. Timestamps live outside the hash so the same computation always hashes identically.
### 18.4 Traceability chain (must be demonstrable in the demo)
```plain text
SOURCE (DOI + table)  ->  PARAMETER (csv row, verification_status)
  ->  COMPUTATION (model artefact sha + solver profile + protocol + config_hash)
    ->  OUTPUT (qNet, Phi, margin, rescue, result_hash + credibility state)
```
The UI provenance panel renders this chain for the currently displayed number, and `POST /report` emits it. `test_report_provenance.py` asserts that no result can be exported with any link in the chain missing.
---
## §19 — BACKEND
### 19.1 Technology (frozen — nothing else may be added)
<table header-row="true">
<tr>
<td>Layer</td>
<td>Choice</td>
<td>Reason</td>
</tr>
<tr>
<td>Language</td>
<td>**Python 3.11**</td>
<td>Myokit + SciPy ecosystem</td>
</tr>
<tr>
<td>Cell-model runtime</td>
<td>**Myokit** (with SUNDIALS/CVODES)</td>
<td>stiff integration, CellML import, state export for warm starts</td>
</tr>
<tr>
<td>Numerics</td>
<td>**NumPy**, **SciPy** (`optimize.brentq`-style bisection is implemented in-house for full control; `minimize(SLSQP)` for Stage C; `integrate.solve_ivp(BDF)` for V-9 only)</td>
<td>minimal dependency surface</td>
</tr>
<tr>
<td>API</td>
<td>**FastAPI**  • **Uvicorn** (single process, `--workers 1`)</td>
<td>typed, local, offline</td>
</tr>
<tr>
<td>Validation</td>
<td>**Pydantic v2**</td>
<td>frozen request/response schemas</td>
</tr>
<tr>
<td>Cache</td>
<td>**SQLite** (stdlib `sqlite3`)</td>
<td>no server, file-based, offline</td>
</tr>
<tr>
<td>Report</td>
<td>**ReportLab** (PDF) + stdlib `json`</td>
<td>offline PDF, no headless browser needed</td>
</tr>
<tr>
<td>Tests</td>
<td>**pytest** (+ `pytest-cov`)</td>
<td>one runner</td>
</tr>
<tr>
<td>Lint/format</td>
<td>**ruff**</td>
<td>one tool</td>
</tr>
</table>
Forbidden: Celery, Redis, Docker Compose multi-service stacks, Postgres, message queues, microservices, ORMs, cloud SDKs, any LLM SDK, any network call at runtime.
### 19.2 Backend module map
```plain text
backend/app/
  main.py                 FastAPI app factory, startup gates (model hash, data provenance), routers
  config.py               loads configs/*.yaml into frozen dataclasses; computes config_hash
  copy/disclaimers.py     frozen user-facing strings (single source of truth)
  schemas/
    common.py             StateSpec, DrugExposure, SolverProfile, Credibility, Provenance
    simulate.py           SimulateRequest / SimulateResponse
    margin.py             MarginRequest / MarginResponse, BindingConstraint
    rescue.py             RescueRequest / RescueResponse, Action, InfeasibilityReport
    blindspot.py          BlindspotRequest / BlindspotResponse
    verify.py             VerifyRequest / VerifyResponse, CheckResult
    report.py             ReportRequest / ReportResponse
  data/
    drug_registry.py      loader + provenance gate (L2)
    scores.py             Tisdale loader + scorer
    scenarios.py          scenario YAML loader
  ep/
    model_loader.py       .mmt load, hash check, label binding assertions, hERG-dynamic disable
    block.py              Hill block + combination rules (§5.4-5.5)
    simulate.py           steady-state pacing, convergence, final-beat extraction (§4)
    biomarkers.py         qNet, APD90, RA flags (§4.7, §8.1, §8.6)
  engines/
    phi.py                Phi evaluation, boundary calibration, monotonicity scan (§8)
    margin.py             Stage A/B/C margin algorithm (§9)
    binding.py            binding constraint + sensitivity (§10)
    rescue.py             action-set construction, exhaustive search, infeasibility (§11-12)
    blindspot.py          sweep + insensitivity intervals (§13)
    verification.py       per-request gates, battery lookup, aggregation (§14)
  services/
    cache.py              SQLite cache (states + results), key derivation
    hashing.py            canonical_json, config/input/result hashes (§18.3)
    provenance.py         provenance record assembly
    report.py             JSON + PDF rendering
    jobs.py               single-threaded job runner with per-endpoint time budgets
    errors.py             error codes -> HTTP mapping
    units.py              unit constants and conversion guards
```
### 19.3 Job execution and limits
One in-process job runner with a global lock per `config_hash` (prevents duplicate identical solves). Every endpoint has a hard wall-clock budget (§23). On budget exhaustion the endpoint returns HTTP 200 with the documented partial result **and** a `budget_exceeded: true` flag plus degraded credibility — never a truncated number presented as complete. Long-running validation batteries are **not** API endpoints; they run via `scripts/run_verification.py`.
### 19.4 Error handling
```plain text
E_SCHEMA(422) E_UNKNOWN_DRUG(400) E_DOMAIN_K(400) E_DOMAIN_EXPOSURE(400) E_DOMAIN_CL(400)
E_PROVENANCE_INCOMPLETE(503, startup abort) E_MODEL_HASH_MISMATCH(503, startup abort)
E_MODEL_BINDING(503, startup abort) E_SOLVER(500) E_NO_STEADY_STATE(422)
E_NUMERICAL_INSTABILITY(422) E_ACTION_SET_TOO_LARGE(500, config error)
E_NO_UPSTROKE(422) E_BUDGET(200 with partial+flag) E_UNITS(503, startup abort)
```
Every error body: `{ "error_code", "message", "detail", "remediation", "disclaimers" }`. No stack traces to the client; full traces to `logs/backend.log`.
### 19.5 Offline operation
At runtime the process opens only: `models/`, `data/`, `configs/`, `validation/`, `cache/`, `logs/`. `scripts/check_offline.py` asserts no outbound socket is created during the full test suite (monkeypatches `socket.socket`), and CI runs the suite with networking disabled.
---
## §20 — API SPECIFICATION
Base URL `http://127.0.0.1:8000/api/v1`. All responses include `provenance`, `credibility`, `disclaimers`, `config_hash`, `result_hash`.
### 20.1 `GET /drugs`
Response: `{ "drugs": [ { "drug_id", "drug_name", "cmax_free_nM", "cmax_source_doi", "channels": [ { "channel", "ic50_nM", "hill", "source_doi", "source_table", "verification_status" } ], "discontinuable", "dose_steps", "cipa_training_risk_label", "qt_risk_class_manual", "max_validated_multiple" } ], "data_integrity": "OK" }`. Errors: `E_PROVENANCE_INCOMPLETE`. Budget 200 ms.
### 20.2 `POST /simulate`
```json
{ "drugs": [{"drug_id": "dofetilide", "exposure_multiplier": 1.0},
             {"drug_id": "verapamil", "exposure_multiplier": 1.0],
  "k_o_mM": 4.0, "cl_ms": 2000, "cell_type": "endo",
  "solver_profile": "standard", "return_trace": true, "combo_rule": "indep_mult" }
```
```json
{ "qnet_C_per_F": 0.0631, "qnet_ctrl_C_per_F": 0.0788, "qnet_boundary_C_per_F": 0.0591,
  "phi_C_per_F": 0.0040, "apd90_ms": 291.4, "v_rest_mV": -87.1, "v_peak_mV": 39.2,
  "dvdt_max_mV_per_ms": 258.0,
  "ra": {"flags": [], "status": "RA_CREDIBLE"},
  "block": {"IKr": 0.41, "ICaL": 0.12, "IKs": 0.0, "Ito": 0.0, "INa_peak": 0.03, "INaL": 0.02},
  "combo_sensitivity": {"rule_alt": "additive_occ", "delta_qnet": 0.0009, "same_side": true},
  "convergence": {"beats_run": 1000, "c1": true, "c2": true, "c3": true, "c4": true},
  "trace": {"dt_ms": 0.1, "t_ms": [], "v_mV": [], "i_net_A_per_F": []},
  "tags": [], "credibility": {"state": "VERIFIED", "checks": {}},
  "cached": false, "compute_ms": 4120 }
```
Errors: `E_UNKNOWN_DRUG`, `E_DOMAIN_*`, `E_NO_STEADY_STATE`, `E_SOLVER`, `E_NUMERICAL_INSTABILITY`. Budget **20 s**. Validation: ≤ 4 drugs, unique drug ids, all domains checked.
### 20.3 `POST /margin`
Request = `/simulate` body **plus** `{ "axes": ["k_o_mM", "exposure:dofetilide"], "weights": {"k_o_mM": 1.0, "exposure:dofetilide": 1.0}, "box_override": null, "max_evals": 300 }`.
```json
{ "phi_now": 0.0040, "m_signed": 1.83, "m_status": "EXACT_AXIS",
  "m_label": "exact along a single axis (bisected to 1e-3 normalised units)",
  "axes": [ {"axis": "k_o_mM", "distance": 1.83, "critical_raw_value": 3.42,
              "direction": "decrease", "monotonicity": "MONOTONIC", "all_roots": [3.42],
              "reachable": true, "sensitivity_share": 0.61},
            {"axis": "exposure:dofetilide", "distance": 2.31, "critical_raw_value": 4.95,
              "direction": "increase", "monotonicity": "MONOTONIC", "all_roots": [4.95],
              "reachable": true, "sensitivity_share": 0.39} ],
  "binding_constraint": {"axis": "k_o_mM", "critical_raw_value": 3.42, "tied_axes": [],
                          "alternative_axis": "exposure:dofetilide",
                          "alternative_critical_value": 4.95,
                          "distance_vs_sensitivity_disagree": false},
  "n_phi_evals": 41, "unit_convention": "1 normalised unit = 1 mM K+ = one doubling of exposure",
  "credibility": {"state": "VERIFIED"}, "disclaimers": ["DISC_MARGIN"] }
```
Errors: as `/simulate`, plus `E_BUDGET` semantics. Budget **90 s** (warm), hard cap 120 s.
### 20.4 `POST /rescue`
Request = `/simulate` body **plus** `{ "tau": 0.05, "cost_weights": {"w_K": 1.0, "w_E": 1.0, "w_D": 6.0}, "allow_discontinuation": true, "compute_post_margin": true }`. Response = the §11.7 contract, extended with the §12.3 `infeasibility` object when applicable. Budget **150 s** (hard cap 180 s); if the budget is hit, status becomes `INCOMPLETE_SEARCH`, never an infeasibility claim.
### 20.5 `POST /blindspot`
```json
{ "base_state": { "...as /simulate..." },
  "sweep": {"variable": "k_o_mM", "from": 5.0, "to": 3.6, "n_points": 21},
  "score_inputs": {"score_id": "tisdale_2013", "age_ge_68": true, "female_sex": "UNKNOWN",
                    "loop_diuretic": true, "admission_qtc_ge_450": "UNKNOWN",
                    "acute_mi": false, "sepsis": false, "heart_failure": true} }
```
Response: `{ "grid": [], "phi": [], "margin": [], "score_min": [], "score_max": [], "score_band": [], "insensitivity_intervals": [{"from": 4.5, "to": 3.6, "band": "moderate", "delta_phi": 0.0071], "crossing_point": 3.9, "verdict": "<§13.4 wording>", "assumptions": ["ASSUMPTION_SERUM_KO_PROXY_v1"], "credibility": {...}, "disclaimers": ["DISC_SCORE"] }`. Budget **120 s**.
### 20.6 `POST /verify`
Request: `{ "scope": "request" | "battery_lookup", "state": {...} }`. Response: `{ "checks": [{"id": "V-1", "name": "...", "tier": "request", "state": "PASS", "detail": "...", "threshold": "...", "observed": "..."}], "aggregate": "VERIFIED", "battery": {"present": true, "config_hash": "...", "run_on": "...", "summary": {"pass": 14, "fail": 0, "unknown": 0}} }`. Budget **10 s** (never runs the heavy battery).
### 20.7 `GET /validation`
Response: the stored battery result for the active `config_hash` plus `validation_cases.yaml` metadata and `reference_values.yaml` statuses. If absent: `{ "present": false, "credibility_implication": "UNVERIFIED" }`. Budget 500 ms.
### 20.8 `POST /report`
Request: `{ "include": ["simulate", "margin", "rescue", "blindspot", "verify"], "state": {...}, "format": ["json", "pdf"], "result_hashes": [] }`. Response: `{ "json": {...}, "pdf_path": "reports/<result_hash>.pdf", "result_hash": "...", "watermark": "NONE|UNVERIFIED|FAILED" }`. Refuses with `E_PROVENANCE_INCOMPLETE` if any provenance link is missing. Budget **30 s** (uses cached results only; never triggers a fresh solve).
### 20.9 `GET /scenarios` and `GET /health`
`/scenarios` lists declared synthetic scenarios (`scenario_id`, title, description, `synthetic: true`, state). `/health` returns `{ "status", "model_id", "model_hash", "config_hash", "data_integrity", "battery_present", "version", "offline": true }`.
### 20.10 API tests
`test_api_simulate.py`, `test_api_margin.py`, `test_api_rescue.py`, `test_api_blindspot.py`, `test_api_verify.py`, `test_api_report.py`, `test_api_errors.py`, `test_api_contract_schema.py` (OpenAPI snapshot committed to `docs/openapi.snapshot.json`; any change must be intentional and reviewed).
---
## §21 — FRONTEND
### 21.1 Technology and constraints
React 18 + TypeScript + Vite; Plotly.js (bundled locally) for traces; CSS modules or a single hand-written stylesheet; **no** UI kit, **no** CDN fonts, **no** animation library, **no** 3D. Dark scientific palette, monospace for numbers, tabular alignment, one accent colour per semantic state (verified/amber/red). Forbidden: cartoon or 3D beating heart, gamified gauges, confetti, pulsing animations, emoji risk faces, red/green traffic lights implying clinical verdicts.
### 21.2 Screen layout (single page, four regions)
```plain text
+---------------------------------------------------------------------------------+
| HEADER: TorsadeTwin | Mechanistic Cardiac Safety Margin + Rescue Engine         |
|         model: ORd-CiPA v1.0 (hash 8f2c..) | config 4ab1.. | OFFLINE | VERIFIED |
|         DISC_GLOBAL banner (always visible, never dismissible)                  |
+----------------+--------------------------------------------+---------------------+
| LEFT (280px)   | CENTER (flex)                              | RIGHT (360px)       |
| Scenario       | Tab 1: Action potential V(t) final beat     | SAFETY MARGIN       |
|  - dropdown    |         + I_net(t) with shaded qNet area   |  M_signed +/- units |
|  - synthetic   | Tab 2: qNet & APD90 vs swept variable      |  gauge = linear bar |
|    badge       |         with boundary line + crossing pt   |  with boundary tick |
| Drugs (<=4)    | Tab 3: Phi(K+) and Phi(exposure) curves    |  status chip        |
|  - checkbox    |         with roots marked                   |  (EXACT_AXIS / <=)  |
|  - exposure    | Tab 4: Rescue table (all |A| rows)         | BINDING CONSTRAINT  |
|    log2 slider |         cost | phi | feasible | credible   |  axis + critical    |
| K+ slider      |                                            |  value + alt axis   |
|  2.5-7.0 mM    | All plots: axis units, no smoothing,       | RESCUE              |
| CL slider      | no interpolation beyond stated dt          |  [Run rescue] btn   |
|  (greyed for   |                                            |  best action card   |
|   margin, with |                                            |  or infeasibility   |
|   CL_EXCLUDED  |                                            |  card w/ reason     |
|   tooltip)     |                                            | DISC_MARGIN caption |
| [Simulate]     |                                            |                     |
| [Margin]       |                                            |                     |
+----------------+--------------------------------------------+---------------------+
| BOTTOM (tabs): MECHANISM | CLINICAL-SCORE COMPARISON | VERIFICATION | PROVENANCE |
|  MECHANISM: per-channel block table (fraction blocked, IC50, Hill, DOI) and      |
|             per-current charge contributions to qNet for the analysis beat        |
|  SCORE:     Tisdale band vs margin over the sweep, insensitivity intervals,       |
|             §13.4 verdict text, DISC_SCORE                                        |
|  VERIFICATION: V-1..V-16 table: id | check | tier | observed | threshold | state  |
|             + battery run date + [Re-run request gates]                           |
|  PROVENANCE: SOURCE -> PARAMETER -> COMPUTATION -> OUTPUT chain, hashes,          |
|             assumption IDs, [Export JSON] [Export PDF]                            |
+---------------------------------------------------------------------------------+
```
### 21.3 Exact state semantics in the UI
<table header-row="true">
<tr>
<td>Element</td>
<td>Rule</td>
</tr>
<tr>
<td>Margin number</td>
<td>shows sign, unit convention text, and `≤` prefix when `m_status = SAMPLED_UB`</td>
</tr>
<tr>
<td>Boundary line</td>
<td>labelled "model-defined boundary (qNet = 75 % of drug-free control — declared convention)"</td>
</tr>
<tr>
<td>Literature threshold band</td>
<td>drawn only as a faint dashed band labelled `literature reference — not numerically comparable (D1)`</td>
</tr>
<tr>
<td>Credibility</td>
<td>header chip + per-panel chip; `UNVERIFIED` → amber banner and muted numbers; `FAILED` → red banner and numbers hidden behind "show anyway (debug)"</td>
</tr>
<tr>
<td>RA/EAD</td>
<td>shown as a small annotation on the trace with its own status; never coloured as a verdict</td>
</tr>
<tr>
<td>Rescue</td>
<td>full evaluated table always available; best action card states cost, resulting Φ, post-rescue margin, and `DISC_RESCUE`</td>
</tr>
<tr>
<td>Infeasibility</td>
<td>card shows status string exactly per §12.2 plus reason code, closest action, shortfall, and `DISC_INFEAS`</td>
</tr>
<tr>
<td>Mg²⁺</td>
<td>a disabled row reading `Mg2+ — NOT MODELLED` with the D4 reason tooltip</td>
</tr>
<tr>
<td>Loading</td>
<td>deterministic progress text (`beats 600/1000`, `actions 7/15`), never a fake spinner percentage</td>
</tr>
</table>
### 21.4 Frontend structure
```plain text
frontend/src/
  App.tsx  api/client.ts  api/types.ts (generated from OpenAPI snapshot)
  components/ ScenarioPanel StatePanel MarginPanel BindingPanel RescuePanel
              APTracePlot SweepPlot PhiCurvePlot MechanismTable ScoreComparison
              VerificationTable ProvenancePanel CredibilityBanner DisclaimerBar
  state/store.ts (single reducer; no global mutable state)
  copy/strings.ts (mirrors backend copy; contract test asserts equality)
  styles/theme.css
```
### 21.5 Tests
`frontend/tests/` (Vitest): `credibility_rendering.test.tsx` (each state renders the mandated banner/watermark), `margin_upper_bound.test.tsx` (`≤` shown for `SAMPLED_UB`), `infeasibility_wording.test.tsx` (status→string mapping), `copy_parity.test.ts` (frontend strings equal backend `copy/disclaimers.py` values), `no_forbidden_phrases.test.ts`.
---
## §22 — KILLER DEMO (EXACT 3-MINUTE SCRIPT)
### 22.1 Demo scenario (declared synthetic, `data/scenarios/demo_a.yaml`)
```yaml
scenario_id: DEMO-A
synthetic: true
title: "Declared synthetic regimen: two QT-relevant agents, K+ initially normal"
state:
  drugs: [{drug_id: dofetilide, exposure_multiplier: 1.0},
          {drug_id: quinidine,  exposure_multiplier: 1.0]
  k_o_mM: 4.5
  cl_ms: 2000
  cell_type: endo
  solver_profile: standard
score_inputs: {score_id: tisdale_2013, age_ge_68: true, loop_diuretic: true,
               heart_failure: true, acute_mi: false, sepsis: false,
               female_sex: UNKNOWN, admission_qtc_ge_450: UNKNOWN}
notes: "No real patient data. Exposures are declared multiples of published free Cmax."
```
If, after the Day-2 data transcription, DEMO-A does not actually cross the boundary inside the K⁺ box, the **scenario** is adjusted (drug pair or multiplier) and re-recorded — never the model, thresholds, or score. `scripts/build_demo_cache.py` prints whether the crossing exists; the chosen scenario is then frozen at feature freeze.
### 22.2 Minute-by-minute
<table header-row="true">
<tr>
<td>t</td>
<td>Step</td>
<td>Action</td>
<td>What is shown</td>
<td>Live or cached</td>
</tr>
<tr>
<td>0:00</td>
<td>1. Baseline</td>
<td>load DEMO-A, click Simulate</td>
<td>AP trace, qNet, APD90, boundary line, `VERIFIED` chip</td>
<td>**cached** (precomputed)</td>
</tr>
<tr>
<td>0:20</td>
<td>2. Compute margin</td>
<td>click Margin</td>
<td>`M_signed = +1.8`, unit convention, `EXACT_AXIS`</td>
<td>**cached**</td>
</tr>
<tr>
<td>0:40</td>
<td>3. Change K⁺</td>
<td>judge drags K⁺ 4.5 → 4.0 → 3.8</td>
<td>sweep plot updates; margin shrinks in real time</td>
<td>**cached grid** (0.1 mM steps precomputed), interpolation **disabled** — slider snaps to computed grid points</td>
</tr>
<tr>
<td>1:00</td>
<td>4. Approach boundary</td>
<td>continue to 3.7</td>
<td>margin → +0.3, amber "approaching boundary" (not a clinical warning)</td>
<td>cached grid</td>
</tr>
<tr>
<td>1:10</td>
<td>5. Cross boundary</td>
<td>K⁺ = 3.6</td>
<td>Φ \< 0, "unsafe side of the model-defined boundary", crossing point annotated (e.g. 3.68 mM)</td>
<td>cached grid</td>
</tr>
<tr>
<td>1:25</td>
<td>6. Clinical score</td>
<td>open SCORE tab</td>
<td>Tisdale band constant across 4.5 → 3.6 while margin crosses; §13.4 verdict</td>
<td>cached</td>
</tr>
<tr>
<td>1:45</td>
<td>7. Verify</td>
<td>open VERIFICATION tab</td>
<td>V-1..V-16 table all `PASS`; battery hash + date; then toggle the `loose_NEGATIVE_CONTROL` demo entry to show a `FAILED` result being refused</td>
<td>cached (both)</td>
</tr>
<tr>
<td>2:05</td>
<td>8. Mechanism</td>
<td>open MECHANISM tab</td>
<td>per-channel block table with IC50 + DOI; per-current charge contributions showing which current lost the charge</td>
<td>cached</td>
</tr>
<tr>
<td>2:20</td>
<td>9. Run Rescue</td>
<td>click Run rescue</td>
<td>all 15 actions with cost/Φ/feasible/credible; best action card (e.g. K⁺ → 4.4 mM, cost 0.8, post-rescue margin +1.1)</td>
<td>**live** on the cached state (≤ 8 s), fallback to cached table if over budget</td>
</tr>
<tr>
<td>2:40</td>
<td>10. Best intervention</td>
<td>expand card</td>
<td>shows `DISC_RESCUE`, cost weights, post-rescue Φ and margin</td>
<td>live/cached</td>
</tr>
<tr>
<td>2:50</td>
<td>11. Infeasible variant</td>
<td>load `DEMO-B` (dofetilide 4×, K⁺ 3.2, both drugs `discontinuable: false`) and click Rescue</td>
<td>`INFEASIBLE_EXHAUSTIVE` card: certificate wording, reason `K_CEILING_BINDING`, closest action, shortfall, `DISC_INFEAS`</td>
<td>**cached**</td>
</tr>
<tr>
<td>3:00</td>
<td>12. Export</td>
<td>click Export JSON + PDF</td>
<td>provenance chain, hashes; re-import shows identical `result_hash`</td>
<td>live (≤ 3 s)</td>
</tr>
</table>
### 22.3 Precompute / cache / live split (frozen)
<table header-row="true">
<tr>
<td>Category</td>
<td>Content</td>
</tr>
<tr>
<td>**Precomputed** (`scripts/build_demo_cache.py`, committed under `cache/demo/`)</td>
<td>DEMO-A and DEMO-B baselines; K⁺ grid 5.4 → 3.0 mM in 0.1 mM steps for both scenarios; exposure grid 0.25×–4× in log₂ quarter-steps for each demo drug; full margin results; full rescue tables; blind-spot sweeps; battery results for the demo `config_hash`</td>
</tr>
<tr>
<td>**Live during the demo**</td>
<td>rescue on the current cached state; report export; per-request verification gates</td>
</tr>
<tr>
<td>**Never live**</td>
<td>the 1000-beat cold solves, the heavy verification battery</td>
</tr>
<tr>
<td>**Latency ceilings**</td>
<td>any click ≤ 2 s from cache; live rescue ≤ 8 s; export ≤ 3 s; page load ≤ 1.5 s</td>
</tr>
</table>
### 22.4 Scientific honesty of the cached demo (mandatory)
Every cached value carries the same `config_hash`, `result_hash` and credibility state it had when computed, and the UI shows a `cached` badge with the computation timestamp. The demo asserts nothing that a live run would not reproduce; `scripts/verify_demo_cache.py` re-runs a random 10 % sample live and fails if any cached number differs beyond `tol_phi`. No internet access is used at any point (A6).
---
## §23 — PERFORMANCE TARGETS
<table header-row="true">
<tr>
<td>Operation</td>
<td>Cold (no cache) target</td>
<td>Warm/cached target</td>
<td>Hard budget (endpoint)</td>
</tr>
<tr>
<td>Startup (model load, hash, data gates)</td>
<td>≤ 5 s</td>
<td>—</td>
<td>abort on failure</td>
</tr>
<tr>
<td>Single steady-state simulation (1000 beats, CL 2000 ms)</td>
<td>≤ 15 s</td>
<td>≤ 0.3 s</td>
<td>20 s</td>
</tr>
<tr>
<td>Warm-started simulation (200 beats)</td>
<td>≤ 4 s</td>
<td>≤ 0.3 s</td>
<td>20 s</td>
</tr>
<tr>
<td>Margin, 1 axis (Stage A only)</td>
<td>≤ 40 s</td>
<td>≤ 0.5 s</td>
<td>120 s</td>
</tr>
<tr>
<td>Margin, 2 axes (Stage A+B+C)</td>
<td>≤ 90 s</td>
<td>≤ 1 s</td>
<td>120 s</td>
</tr>
<tr>
<td>Rescue (`|A| = 15`, warm starts)</td>
<td>≤ 90 s</td>
<td>≤ 2 s</td>
<td>180 s</td>
</tr>
<tr>
<td>Blind-spot sweep (21 points)</td>
<td>≤ 90 s</td>
<td>≤ 1.5 s</td>
<td>120 s</td>
</tr>
<tr>
<td>Verification: request gates</td>
<td>≤ 0.1 s</td>
<td>—</td>
<td>10 s</td>
</tr>
<tr>
<td>Verification battery (offline)</td>
<td>≤ 30 min</td>
<td>—</td>
<td>n/a (script)</td>
</tr>
<tr>
<td>Report export</td>
<td>≤ 3 s</td>
<td>≤ 3 s</td>
<td>30 s</td>
</tr>
</table>
Reference hardware: 4-core laptop CPU, 8 GB RAM, no GPU. If cold targets are missed, the permitted levers are (in order): enable warm starts, reduce `n_prepace` **only** if C1–C4 still pass, reduce the number of sampled directions in Stage B (which changes `M_status` labelling), and precompute more of the demo. Loosening solver tolerances to gain speed is **forbidden** (it would break V-8).
---
## §24 — FAILURE MODES
<table header-row="true">
<tr>
<td>Failure</td>
<td>Detection</td>
<td>UI response</td>
<td>Fallback</td>
</tr>
<tr>
<td>Model file missing / hash mismatch</td>
<td>startup SHA-256 check</td>
<td>full-screen blocking error with the expected/actual hash</td>
<td>refuse to start; `scripts/convert_model.py` re-run instructions</td>
</tr>
<tr>
<td>CellML import fails</td>
<td>`convert_model.py` non-zero exit</td>
<td>build-time failure, `docs/FALLBACK_INVOKED.md` required</td>
<td>documented ORd-2011 fallback (§3.4) with banner + reference re-recording</td>
</tr>
<tr>
<td>Missing model label binding</td>
<td>startup assertion</td>
<td>blocking error naming the missing label</td>
<td>refuse to start</td>
</tr>
<tr>
<td>Invalid parameter / out-of-domain input</td>
<td>Pydantic + domain gate (L1)</td>
<td>inline field error with permitted range and the range's source</td>
<td>request rejected, previous result retained</td>
</tr>
<tr>
<td>Drug data incomplete / not `VERIFIED`</td>
<td>L2 provenance gate</td>
<td>blocking startup error listing offending rows</td>
<td>refuse to serve `/drugs`, `/simulate`</td>
</tr>
<tr>
<td>Non-convergence to steady state</td>
<td>C1–C4 after `n_prepace + n_extra_max`</td>
<td>red `FAILED` banner, "steady state not reached", no margin</td>
<td>show convergence diagnostics; suggest `tight` profile; margin/rescue disabled</td>
</tr>
<tr>
<td>Numerical instability (`NaN`/`inf`, V blow-up)</td>
<td>trace scan</td>
<td>red `FAILED`, trace shown for debugging only</td>
<td>discard result, do not cache, log full state</td>
</tr>
<tr>
<td>Unknown drug data (channel `NA`)</td>
<td>registry flag</td>
<td>`partial_panel` chip listing channels with no data</td>
<td>proceed with zero block on those channels, credibility ≤ `UNVERIFIED`</td>
</tr>
<tr>
<td>Out-of-calibrated concentration</td>
<td>exposure \> `max_validated_multiple`</td>
<td>amber tag `OUT_OF_CALIBRATED_RANGE` on every derived number</td>
<td>compute but never mark `VERIFIED`</td>
</tr>
<tr>
<td>Non-monotone Φ</td>
<td>§8.5 scan</td>
<td>badge `NON_MONOTONIC`, all roots plotted</td>
<td>nearest root drives the margin; binding constraint still computed</td>
</tr>
<tr>
<td>Margin budget exhausted</td>
<td>eval counter</td>
<td>`BUDGET_EXCEEDED` chip, axis-only results</td>
<td>Stage A results only, credibility ≤ `UNVERIFIED`</td>
</tr>
<tr>
<td>Rescue infeasible</td>
<td>§12 classification</td>
<td>infeasibility card with the exact permitted wording</td>
<td>show closest action + shortfall + out-of-scope note</td>
</tr>
<tr>
<td>Unsupported / out-of-box action requested</td>
<td>action builder</td>
<td>action row marked `SKIPPED_OUT_OF_BOX`</td>
<td>status forced to `INCOMPLETE_SEARCH`</td>
</tr>
<tr>
<td>Verification battery absent for `config_hash`</td>
<td>battery lookup</td>
<td>amber `UNVERIFIED`, "battery not run for this configuration"</td>
<td>offer the exact command to run it</td>
</tr>
<tr>
<td>Verification check FAIL</td>
<td>aggregation</td>
<td>red `FAILED`, numbers behind debug toggle</td>
<td>no verdict rendered, export watermarked</td>
</tr>
<tr>
<td>Combination-rule sensitivity flips side</td>
<td>§5.5 sensitivity</td>
<td>amber `COMBO_RULE_SENSITIVE` with both Φ values</td>
<td>credibility capped at `UNVERIFIED`</td>
</tr>
<tr>
<td>Cache corruption / schema drift</td>
<td>cache row `code_version` mismatch</td>
<td>silent, logged</td>
<td>ignore stale rows and recompute</td>
</tr>
<tr>
<td>Endpoint timeout</td>
<td>wall-clock budget</td>
<td>deterministic partial result + `budget_exceeded` flag</td>
<td>degraded credibility; never a completeness claim</td>
</tr>
</table>
Principle: **fail loud, fail labelled, never fail green.**
---
## §25 — SAFETY / CLAIMS
### 25.1 What we CAN claim (approved sentences — use verbatim)
1. "TorsadeTwin computes, for a declared modelled state, the distance to a model-defined repolarization-risk boundary defined on qNet in a published human ventricular myocyte model."
2. "It identifies which modelled variable reaches that boundary first within declared bounds."
3. "It exhaustively searches a declared finite set of permitted single actions for the minimum-cost action that restores a declared target margin, and reports when no element of that set does."
4. "It attaches a numerical credibility state to every result and refuses to present results that fail its verification gates as verified."
5. "Every number is traceable to a cited source, a model artefact hash, a solver configuration and a reproducible result hash."
6. "The system reproduces the qualitative direction and ordering expected from published in-silico cardiac safety work for the drugs and conditions tested (see §16)."
7. "This is a mechanistic computational research prototype for hypothesis generation and methodology demonstration."
### 25.2 What we CANNOT claim (forbidden — in speech, slides, UI, code and README)
The canonical prohibited-language list is defined in `backend/app/copy/disclaimers.py` and mechanically enforced throughout the repository. Do not reproduce its entries, including as quoted examples.
<callout icon="🛡️" color="yellow_bg">
	Note on the product name: "Twin" refers to a **cell-level mechanistic model twin of a declared synthetic state**, not a patient digital twin. The UI subtitle and README must state this explicitly so the name cannot be read as a personalised-medicine claim.
</callout>
### 25.3 Preferred framing vocabulary
mechanistic simulation · in-silico research prototype · model-defined safety margin · model-defined boundary · declared finite action set · exhaustive-domain infeasibility · hypothesis generation · reproducible in-silico analysis · numerical credibility gate · not a clinical decision-making device.
### 25.4 Enforcement
`test_copy_forbidden_phrases.py` scans `backend/`, `frontend/src/`, `docs/`, `README.md` and the slide-text file `docs/DEMO_SCRIPT.md` for the §25.2 list (case-insensitive, whitespace-normalised) and fails CI on any match. The disclaimer bar is non-dismissible in the DOM (asserted by a frontend test).
---
## §26 — TEST SUITE
### 26.1 Layout and gates
```plain text
tests/
  unit/          fast, no simulation (< 30 s total)
  numerics/      short simulations, tolerance-based (< 10 min)
  integration/   full pipeline through engines (< 20 min)
  api/           FastAPI TestClient (< 3 min)
  validation/    the §16 battery, marked slow, run nightly / pre-demo
  failure/       negative controls (§17)
  repro/         hash stability and determinism
  contract/      frontend-backend schema and copy parity
```
CI gate for every commit: `unit + api + failure + repro + contract`. Pre-demo gate: **everything**, including `validation` and `numerics`.
### 26.2 Key test files (exact names — implement all)
<table header-row="true">
<tr>
<td>Category</td>
<td>Files</td>
</tr>
<tr>
<td>Unit</td>
<td>`test_inputs_validation.py`, `test_domains.py`, `test_hill_block.py`, `test_combination_rule.py`, `test_drug_registry.py`, `test_tisdale_scoring.py`, `test_hashing_canonical_json.py`, `test_units.py`, `test_cost_function.py`, `test_action_set_builder.py`, `test_copy_forbidden_phrases.py`, `test_infeasibility_language.py`</td>
</tr>
<tr>
<td>Numerics</td>
<td>`test_ep_engine.py`, `test_steady_state.py`, `test_biomarkers.py`, `test_quadrature.py`, `test_apd90_edge_cases.py`, `test_ko_pathway.py`, `test_solver_profiles.py`</td>
</tr>
<tr>
<td>Engines (analytic surrogates)</td>
<td>`test_phi_monotonicity_scan.py`, `test_margin_engine.py`, `test_margin_monotonicity.py`, `test_margin_budget.py`, `test_binding_constraint.py`, `test_rescue_engine.py`, `test_rescue_exhaustive.py`, `test_rescue_post_margin.py`, `test_rescue_determinism.py`, `test_rescue_out_of_box.py`, `test_infeasibility_certificate.py`, `test_blindspot_auditor.py`</td>
</tr>
<tr>
<td>Integration</td>
<td>`test_pipeline_simulate_to_margin.py`, `test_pipeline_margin_to_rescue.py`, `test_pipeline_blindspot.py`, `test_cache_behaviour.py`, `test_warm_start_equivalence.py`</td>
</tr>
<tr>
<td>Model integrity</td>
<td>`test_model_bindings.py`, `test_model_state_list.py`, `test_model_scaling_audit.py`, `test_herg_dynamic_disabled.py`, `test_model_hash.py`</td>
</tr>
<tr>
<td>Verification</td>
<td>`test_verification_engine.py`, `test_verification_missing_battery.py`, `test_display_rules.py`</td>
</tr>
<tr>
<td>Validation (§16)</td>
<td>`test_e1_control.py`, `test_e2_drug_direction.py`, `test_e3_prior_art_ordering.py`, `test_e4_k_directionality.py`, `test_e5_numerical_sensitivity.py`, `test_e6_margin_consistency.py`, `test_e7_rescue_consistency.py`, `test_e8_infeasibility.py`, `test_e9_blindspot.py`</td>
</tr>
<tr>
<td>Failure / negative controls</td>
<td>`test_negative_controls.py`, `test_negative_control_bad_drug_csv.py`, `test_no_redistributed_licensed_data.py`, `test_api_errors.py`, `test_offline_no_network.py`</td>
</tr>
<tr>
<td>Reproducibility</td>
<td>`test_reproducibility.py`, `test_result_hash_stability.py`, `test_golden_regression.py`, `test_demo_cache_integrity.py`</td>
</tr>
<tr>
<td>API / contract</td>
<td>`test_api_simulate.py`, `test_api_margin.py`, `test_api_rescue.py`, `test_api_blindspot.py`, `test_api_verify.py`, `test_api_report.py`, `test_api_contract_schema.py`, `test_report_provenance.py`</td>
</tr>
<tr>
<td>Frontend (Vitest)</td>
<td>`credibility_rendering.test.tsx`, `margin_upper_bound.test.tsx`, `infeasibility_wording.test.tsx`, `copy_parity.test.ts`, `no_forbidden_phrases.test.ts`, `plot_units.test.tsx`</td>
</tr>
</table>
### 26.3 Testing rules
1. Algorithm correctness (margin, binding, rescue, infeasibility) is proven against **analytic surrogate Φ functions** where the answer is known in closed form — not against the cell model. The cell model is validated separately (§16).
2. Numerical tests use explicit tolerances taken from this document; no test may invent a looser tolerance to pass.
3. Golden regression files live in `validation/golden/` and may only change with a recorded justification in `validation/GOLDEN_CHANGELOG.md`.
4. Coverage target: ≥ 85 % on `backend/app/engines/` and `backend/app/ep/`; a coverage drop fails CI.
5. Every failure path in §24 has at least one test.
---
## §27 — REPOSITORY STRUCTURE (COMPLETE TREE)
```plain text
torsadetwin/
  README.md                          product framing + DISC_GLOBAL + "not a medical device"
  LICENSE
  pyproject.toml                     pinned deps, ruff + pytest config
  Makefile                           setup, fetch-model, convert-model, test, battery, demo-cache, run
  .github/workflows/ci.yml           unit+api+failure+repro+contract, network disabled
  configs/
    model.yaml                       model_id, artefact paths, apply_dutta_scaling, cell_type
    solver.yaml                      profiles: standard | tight | loose_NEGATIVE_CONTROL | coarse_log
    protocol.yaml                    cl_ms, n_prepace, n_extra_max, n_warm, stimulus, dt_log
    domains.yaml                     k_o range/default/plausible band, exposure range, cl range + rationale
    thresholds.yaml                  rho, literature_reference block (usable_as_boundary: false)
    margin.yaml                      axes, weights W, box, tolerances, N_scan, directions, max_evals
    rescue.yaml                      tau, action grids, cost weights, |A| cap
    runtime.yaml                     warm_start, cache path, budgets, log level
    state_scales.yaml                per-state eps_i for C2 (generated once, committed)
  models/
    vendor/ohara_rudy_cipa_v1_2017.cellml
    vendor/CHECKSUMS.txt  vendor/PROVENANCE.yaml  vendor/LICENSE_NOTES.md
    ord_cipa_v1.mmt                  committed converted model (runtime artefact)
    ord_2011_endo.mmt                fallback artefact (§3.4)
    generated/ord_rhs.py             Myokit Python export, used ONLY by V-9
    CHECKSUMS.txt  STATE_VARIABLES.md  SCALING_AUDIT.md
  data/
    drug_parameters.csv              per drug x channel IC50/Hill + provenance (§5.2)
    drug_registry.yaml               per drug metadata (§5.3)
    scores/tisdale.yaml              transcribed score definition (§13.2)
    scenarios/demo_a.yaml  scenarios/demo_b.yaml  scenarios/control.yaml
    FORBIDDEN_MANIFEST.txt           files that must never exist (licensed data)
  backend/
    app/  (module map exactly as §19.2)
    requirements.txt
  frontend/
    package.json  vite.config.ts  index.html
    src/  (structure exactly as §21.4)
    tests/  (files exactly as §21.5)
  validation/
    validation_cases.yaml            §15.3
    reference_values.yaml            recorded reference numbers + status
    battery_results/<config_hash>.json
    golden/                          golden result hashes and numeric snapshots
    transcription_log.md             who transcribed which parameter, and the reviewer
    GOLDEN_CHANGELOG.md
    REPORT.md                        human-readable battery report
  scripts/
    fetch_model.py                   ONE-TIME network step (build only)
    convert_model.py                 CellML -> .mmt, state dump, scaling audit, Python export
    run_verification.py              the §16 battery -> battery_results/
    build_demo_cache.py              precompute demo grids (§22.3)
    verify_demo_cache.py             live re-check of 10 % of cached values
    verify_data_integrity.py         provenance + forbidden-manifest checks
    check_offline.py                 asserts no runtime network access
    export_report.py                 CLI report generation
  tests/                             layout exactly as §26.1, files as §26.2
  docs/
    SPEC.md                          this document (frozen copy)
    REFERENCES.json  REFERENCES.md   §18.1 citation register
    CLAIMS.md                        §25 approved/forbidden language
    DEMO_SCRIPT.md                   §22 script (scanned by the copy test)
    JUDGE_QA.md                      §31
    ARCHITECTURE.md                  §2 diagram + component contracts
    FALLBACK_INVOKED.md              created only if the fallback model is used
    openapi.snapshot.json            contract-test baseline
    DEVIATION_REGISTER.md            §0.3 plus any newly recorded deviation
  cache/
    torsadetwin.sqlite               runtime cache (gitignored)
    demo/                            committed precomputed demo artefacts
  logs/                              gitignored
  reports/                           generated exports (gitignored)
```
---
## §28 — TEAM PARALLELIZATION
<table header-row="true">
<tr>
<td>Stream</td>
<td>Owner scope</td>
<td>Deliverables</td>
<td>Depends on</td>
<td>Must NOT touch</td>
</tr>
<tr>
<td>**A — Cardiac engine**</td>
<td>model fetch/convert, `ep/*`, solver profiles, steady state, biomarkers</td>
<td>working `simulate()` returning qNet/APD90/RA + diagnostics; `models/*` artefacts and audits</td>
<td>nothing (starts first)</td>
<td>engines/, frontend/</td>
</tr>
<tr>
<td>**B — Drug & data**</td>
<td>`data/*`, `data/drug_registry.py`, `scores.py`, transcription + double-entry</td>
<td>`drug_parameters.csv` fully `VERIFIED`, `tisdale.yaml` transcribed, scenarios, `REFERENCES.json`</td>
<td>nothing (starts first)</td>
<td>ep/, engines/</td>
</tr>
<tr>
<td>**C — Validation & verification**</td>
<td>`engines/verification.py`, `scripts/run_verification.py`, `validation/*`, negative controls</td>
<td>battery runner, `reference_values.yaml` recorded, all §17 controls failing correctly</td>
<td>A (needs `simulate`), B (needs parameters)</td>
<td>engines/margin.py, rescue.py</td>
</tr>
<tr>
<td>**D — Margin & rescue**</td>
<td>`engines/phi.py`, `margin.py`, `binding.py`, `rescue.py`, analytic-surrogate tests</td>
<td>margin, binding constraint, rescue, infeasibility taxonomy, all engine tests green on surrogates</td>
<td>A (interface only — can develop against a stub Φ)</td>
<td>ep/, data/</td>
</tr>
<tr>
<td>**E — Frontend**</td>
<td>`frontend/*`</td>
<td>full 4-region UI against the OpenAPI snapshot with a mock server, then live</td>
<td>API schema freeze (Day 2)</td>
<td>backend/ internals</td>
</tr>
<tr>
<td>**F — Integration & demo**</td>
<td>`main.py`, routers, cache, hashing, provenance, report, demo cache, demo script, judge QA</td>
<td>running app, exports, precomputed demo, `DEMO_SCRIPT.md`, `JUDGE_QA.md`</td>
<td>all</td>
<td>algorithm internals</td>
</tr>
</table>
Anti-duplication rules: Φ is implemented **once** (D) and consumed by C and F; disclaimers exist **once** (F owns `copy/disclaimers.py`, E mirrors via the parity test); schemas are owned by F and frozen at the Day-2 checkpoint; nobody but A edits `models/`, nobody but B edits `data/`.
---
## §29 — 7-DAY BUILD PLAN
<table header-row="true">
<tr>
<td>Day</td>
<td>Must-have deliverables</td>
<td>Parallel tasks</td>
<td>Integration checkpoint</td>
<td>Risk</td>
<td>Fallback</td>
</tr>
<tr>
<td>**1**</td>
<td>Repo skeleton, configs, model fetched + converted, `.mmt` committed with hashes, state list + scaling audit recorded; drug CSV/registry skeleton with the transcription task started; Pydantic schemas drafted</td>
<td>A: fetch/convert/load; B: transcription; D: Φ stub + surrogate tests; E: layout shell with mock data; F: repo, CI, copy module</td>
<td>**CP1 (end of day):** `python -c "load model; run 10 beats"` works and prints APD90</td>
<td>CellML import failure</td>
<td>ORd-2011 fallback (§3.4), record in `FALLBACK_INVOKED.md`</td>
</tr>
<tr>
<td>**2**</td>
<td>Steady-state pacing + convergence C1–C4; qNet + APD90 + RA implemented and unit-tested; **API schema freeze**; drug parameters fully transcribed and double-entered</td>
<td>A: steady state + biomarkers; B: finish transcription, reviewer sign-off; C: `reference_values.yaml` scaffold; D: margin Stage A on surrogates; E: plots vs OpenAPI snapshot; F: `/simulate`  • cache</td>
<td>**CP2:** `POST /simulate` returns real numbers; OpenAPI snapshot committed</td>
<td>slow solves</td>
<td>enable warm start; reduce `n_prepace` only if C1–C4 hold</td>
</tr>
<tr>
<td>**3**</td>
<td>E1 control + E2 drug direction + E4 K⁺ directionality passing or explicitly `UNKNOWN`; Φ and boundary calibration live; margin Stage A on the real model</td>
<td>A: performance + caching; B: scenarios; C: E1/E2/E4; D: margin + binding on real Φ; E: margin/binding panels; F: `/margin`</td>
<td>**CP3:** margin + binding constraint returned for DEMO-A</td>
<td>control values not reproducible</td>
<td>keep checks `UNKNOWN`, never `PASS`; investigate protocol/stimulus first</td>
</tr>
<tr>
<td>**4**</td>
<td>Rescue engine with exhaustive enumeration; §12 status taxonomy + wording tests; blind-spot auditor; DEMO-B infeasible scenario constructed</td>
<td>C: E5 sensitivity + negative controls; D: rescue + infeasibility; E: rescue + score panels; F: `/rescue`, `/blindspot`</td>
<td>**CP4:** feasible rescue on DEMO-A and `INFEASIBLE_EXHAUSTIVE` on DEMO-B</td>
<td>no scenario reaches infeasibility</td>
<td>tighten `tau` or set `discontinuable: false` in the *declared scenario*, never change the model</td>
</tr>
<tr>
<td>**5**</td>
<td>Verification engine wired end-to-end (per-request + battery lookup); full battery run; report JSON + PDF; provenance chain</td>
<td>C: full battery, V-9 cross-solver; D: margin Stage B/C + budgets; E: verification + provenance panels; F: `/verify`, `/validation`, `/report`</td>
<td>**CP5 — FEATURE FREEZE (end of day):** all endpoints live, credibility states rendered. **No new features after this point.**</td>
<td>V-9 cross-solver mismatch</td>
<td>mark V-9 `UNKNOWN` (→ `UNVERIFIED`), document; do not fake a pass</td>
</tr>
<tr>
<td>**6**</td>
<td>Demo cache built and integrity-checked; full test suite green; demo script rehearsed twice; judge QA written; docs complete</td>
<td>all streams: bug-fix, polish, docs, `DEMO_SCRIPT.md`, `JUDGE_QA.md`</td>
<td>**CP6:** end-to-end 3-minute run under latency ceilings, offline (wifi off)</td>
<td>latency overruns</td>
<td>expand precompute per §22.3; never loosen tolerances</td>
</tr>
<tr>
<td>**7**</td>
<td>Frozen build tag, offline rehearsal on the demo machine, backup laptop + exported artefacts, contingency for a dead backend (static exported report + screenshots)</td>
<td>rehearsal, contingency drills, README/claims final read-through</td>
<td>**CP7:** signed-off freeze; only bug fixes with a written justification</td>
<td>demo machine failure</td>
<td>second machine with the same commit + cache; static PDF/JSON fallback</td>
</tr>
</table>
Hard rule: after CP5 (feature freeze) the only permitted changes are bug fixes, test additions, documentation and demo-cache regeneration. Any new feature request is recorded in `docs/DEVIATION_REGISTER.md` as **rejected — post-freeze**.
---
## §30 — MVP / IMPRESSIVE / OVERREACH
### 30.1 MVP — minimum defensible product (must exist or the project has no claim)
1. Vendored ORd-CiPA v1.0 running to steady state with committed hashes and convergence checks.
2. Hill block for at least **3** fully-transcribed drugs (dofetilide, verapamil, diltiazem) with DOIs.
3. qNet + APD90 + internally calibrated boundary + Φ.
4. Margin on **one** axis (K⁺) with exact bisection and a binding-constraint report.
5. Rescue over the K⁺-correction action set with exhaustive enumeration and the §12 status taxonomy.
6. Credibility states with V-1..V-5 request gates and honest `UNKNOWN` handling.
7. `/simulate`, `/margin`, `/rescue`, `/verify` + a UI that renders margin, binding constraint, rescue and credibility.
8. Reproducible report export with the provenance chain.
### 30.2 IMPRESSIVE — present this if the core works
All 6 drugs; 2-axis margin (K⁺ + exposure) with Stage B/C and honest `≤` labelling; full 15-action rescue including discontinuation; DEMO-B exhaustive infeasibility with the reason payload; blind-spot auditor with the §13.4 verdict; full V-1..V-16 battery including the V-9 cross-solver check and live negative-control demonstration; per-current charge attribution; combination-rule sensitivity panel; cached-grid live K⁺ scrubbing; PDF report with hashes.
### 30.3 OVERREACH — forbidden within the 7 days
Dynamic hERG binding re-implementation; multi-action rescue; drug substitution search; population of models; PBPK; tissue/1D/2D; ECG/QT reconstruction; ML risk prediction; chatbot/LLM anywhere in compute; user accounts/cloud/deployment; more than 6 drugs; Mg²⁺; epi/mid cell types; additional biomarkers; mobile/responsive redesign; real patient data of any kind.
---
## §31 — JUDGE ATTACKS (HOSTILE Q&A — ANSWER IN THESE WORDS)
**1. Isn't this just CiPA?**<br>No — and we use CiPA as prior art deliberately. CiPA is a forward risk-assessment paradigm: given a drug at 1–4× C_max, compute qNet and classify the drug. We consume that machinery and add an inverse layer: given a *state* (drugs plus electrolytes), compute the distance to a model-defined boundary, the binding variable, and the minimum permitted single action that restores a target margin — or exhaustively show that no permitted single action does. CiPA does not ask or answer those questions.
**2. Isn't this just ApPredict?**<br>ApPredict/AP-Portal computes forward APD/qNet changes for drug-block inputs. It is a simulator front-end. We do not compete with its physiology; we wrap a constrained inverse solver, a declared finite action search with infeasibility classification, and a credibility gate around that class of forward engine.
**3. Isn't this just Myokit?**<br>Myokit is our ODE/CVODES runtime, like NumPy is a dependency. It is explicitly credited. It provides no margin, no binding-constraint identification, no rescue search, and no infeasibility semantics.
**4. Isn't this just Certara/Simcyp?**<br>Commercial platforms do forward cardiac safety simulation, often with PBPK, at far greater scope and validation. They are closed, licensed and not reproducible line-by-line. We claim neither their scope nor their validation. Our claim is a specific, open, reproducible inverse computation with explicit infeasibility semantics and a numerical credibility gate on every result.
**5. What exactly is novel?**<br>One sentence: the system-level composition of (a) a signed weighted-distance margin to a model-defined qNet boundary in a declared state space, (b) computed binding-constraint identification, (c) a minimum-cost search over a declared finite action set, (d) an explicit distinction between exhaustive finite-domain infeasibility and "no solution found", each result gated by a numerical credibility state. Every underlying component — ORd, qNet, Hill block, APD90, Tisdale — is prior art and is cited as such.
**6. Is your margin validated?**<br>No, and we never say it is. The *algorithm* is verified: it recovers closed-form distances on analytic surrogate functions, and its root-finding is reproducible to declared tolerances. The *clinical meaning* of the margin is unvalidated. It is a distance in modelled-state space, not a probability of harm. Validating it clinically would require outcome data we do not have and do not claim.
**7. Can a single cell predict TdP?**<br>No. Single-cell models cannot represent re-entry, tissue heterogeneity or conduction, and TdP is a tissue-level phenomenon. That is precisely why our functional is a *model-defined repolarization-risk boundary* on qNet, not a TdP prediction, and why every output carries that language and disclaimer.
**8. How do you know your EAD isn't a numerical artifact?**<br>We assume it might be. EAD/RA detection is deliberately **not** part of the margin definition — the margin is defined on the smooth qNet integral. Any RA flag must reproduce under the tight solver profile and a finer log grid, or it is labelled `ARTEFACT_SUSPECTED` and cannot appear as verified. Our negative-control suite deliberately manufactures an artefact under loose settings and requires the system to reject it.
**9. Where do IC50 values come from?**<br>Published multichannel manual-patch data (Crumb et al. 2016, doi:10.1016/j.vascn.2016.03.009), transcribed by a human, double-entered by a second team member, stored with DOI, table reference and a verification status. The API refuses to serve any parameter that is not `VERIFIED`. No values are generated, recalled or interpolated by a language model.
**10. What combination assumption are you making?**<br>Independent, non-competitive block with fractional effects multiplied per channel (`COMBO_RULE_INDEP_MULT_v1`). We label it an assumption, not a validated law, and we compute an additive-occupancy alternative for every result. If the two rules place the state on opposite sides of the boundary, the result's credibility is capped at `UNVERIFIED`.
**11. What happens outside the validated range?**<br>Inputs outside declared domains are rejected. Inputs inside the model domain but outside the calibrated band (for example exposure above 25× free C_max, or K⁺ outside 3.0–5.5 mM) are computed but permanently tagged `OUT_OF_CALIBRATED_RANGE` / `OUT_OF_PHYSIOLOGICAL_RANGE` and can never reach `VERIFIED`.
**12. Why should we trust the rescue action?**<br>Trust it only as a model statement. It says: within this model, this declared action set and this cost ordering, this is the cheapest single action whose recomputed Φ meets the target. We independently recompute the post-action state and its margin, we show the full evaluated table for every action, and we label the cost weights as a declared search preference rather than a clinical judgement. It is explicitly not a treatment recommendation.
**13. What does infeasibility actually mean?**<br>Exactly one thing: every element of a finite, declared, published-in-the-report action set was evaluated, all evaluations passed the credibility gate, and none reached the target margin. That is complete with respect to that set — not a proof about physiology, actions outside the set, or combinations of actions. If any evaluation is missing, non-credible or numerically borderline, we downgrade the wording to "no feasible single intervention found within the defined search domain", and the word *certificate* is removed by code, not by discipline.
**14. Why not just use Tisdale?**<br>Use it — it is validated for its purpose, and we compute it. Our point is narrower and measurable: it is an ordinal score with threshold items, so over K⁺ 4.5 → 3.6 mM its band can remain constant while a mechanistic quantity in this model moves substantially and crosses the model-defined boundary. We report that as *insensitivity of the score to a modelled variable over an interval*. We do not judge the score's correctness or claim clinical superiority for our margin.
**15. Why can't ChatGPT do this?**<br>Because the answer is the output of a stiff ODE solve iterated by a root-finder and an exhaustive search — roughly 40–300 steady-state simulations per query, each hash-reproducible to declared tolerances. A language model can neither integrate the ODEs nor guarantee the enumeration; and no LLM appears anywhere in our compute path.
**16. Are you giving clinical advice?**<br>No. There are no patient records, no doses in clinical units, no infusion rates, no recommendation verbs, and no clinical risk probabilities anywhere in the system. Scenarios are declared synthetic states. Every screen and export carries the frozen global research disclaimer defined in the copy module, and a CI test fails the build if prohibited claim language appears anywhere in the repository.
---
## §32 — FINAL BUILD CONTRACT
**To the implementing model:** implement §0–§31 exactly. You are contracted to build, not to redesign.
<table header-row="true">
<tr>
<td>Contract item</td>
<td>Binding statement</td>
</tr>
<tr>
<td>WHAT TO BUILD</td>
<td>The 12 layers of §2 with the algorithms of §4, §5, §8–§14, the API of §20, the UI of §21, the tests of §26, the repository of §27.</td>
</tr>
<tr>
<td>WHAT NOT TO BUILD</td>
<td>Everything in §1.7 and §30.3. Do not add features, biomarkers, drugs, endpoints, action classes or physiological variables.</td>
</tr>
<tr>
<td>EXACT DATA</td>
<td>`data/drug_parameters.csv`, `data/drug_registry.yaml`, `data/scores/tisdale.yaml`, `data/scenarios/*.yaml`, `validation/*`. Numeric pharmacology values are transcribed by humans; if a value is absent it stays `PLACEHOLDER` and the API refuses to serve it. **Never invent, recall or interpolate a pharmacological or physiological number.**</td>
</tr>
<tr>
<td>EXACT MODELS</td>
<td>`ORd-CiPA-v1.0` from the Physiome CellML exposure, converted to `models/ord_cipa_v1.mmt`, hash-verified, dynamic hERG binding disabled (D1). Only fallback: `ORd2011-endo`, only on documented failure, with a persistent UI banner.</td>
</tr>
<tr>
<td>EXACT ALGORITHMS</td>
<td>Hill block §5.4; multiplicative combination §5.5; qNet §8.1; boundary `rho = 0.75` §8.4; `Φ = qNet − qNet_boundary` §8.5; margin Stages A/B/C §9.4; binding constraint §10.2; exhaustive rescue §11.5; infeasibility taxonomy §12.2; blind-spot sweep §13.3; credibility aggregation §14.3.</td>
</tr>
<tr>
<td>EXACT APIs</td>
<td>The nine endpoints of §20 with the given request/response fields, error codes and budgets. `docs/openapi.snapshot.json` is the contract.</td>
</tr>
<tr>
<td>EXACT UI</td>
<td>The four-region layout of §21.2 with the state semantics of §21.3. No cartoon heart, no 3D, no gamification, no animation, no traffic-light clinical verdicts.</td>
</tr>
<tr>
<td>EXACT TESTS</td>
<td>Every file named in §26.2, with the tolerances stated in this document. No test may loosen a tolerance to pass.</td>
</tr>
<tr>
<td>EXACT VALIDATION</td>
<td>Experiments E1–E9 (§16) plus negative controls N-1–N-9 (§17), gates V-1–V-16 (§14.2), `UNKNOWN` never coerced to `PASS`.</td>
</tr>
<tr>
<td>EXACT DEMO</td>
<td>The 12-step, 3-minute script of §22 with the precompute/live split of §22.3 and the latency ceilings of §23, fully offline.</td>
</tr>
<tr>
<td>LANGUAGE</td>
<td>§25 is binding. `test_copy_forbidden_phrases.py` and `test_infeasibility_language.py` must pass.</td>
</tr>
<tr>
<td>DEVIATIONS</td>
<td>Any genuine contradiction discovered during implementation must be recorded in `docs/DEVIATION_REGISTER.md` with the tension, the resolution and the consequence — then implemented. Silent deviation is a build failure.</td>
</tr>
</table>
<callout icon="🔒" color="red_bg">
	**DO NOT CHANGE THIS ARCHITECTURE.** The margin must be defined on qNet, not on EAD. The boundary must be internally calibrated, not taken from published CiPA thresholds. The rescue search must be exhaustive over a finite declared set. The word "certificate" may only appear for `INFEASIBLE_EXHAUSTIVE`. No LLM may enter the compute path. The system must run offline. Every result must carry a credibility state.
</callout>
---
# FINAL SUMMARIES
## 1. FINAL SYSTEM SUMMARY
TorsadeTwin is an offline, deterministic, in-silico research prototype. It runs the vendored CiPA-optimised O'Hara–Rudy human ventricular myocyte model (ORd-CiPA v1.0, from the Physiome CellML exposure, hosted in Myokit/CVODES) to steady state under a declared synthetic state consisting of up to four drugs at declared multiples of published free C_max plus extracellular K⁺. It applies published multichannel Hill pore-block, computes qNet (primary), APD90 (secondary) and a repolarization-abnormality annotation (tertiary, never definitional). It defines `Φ = qNet − 0.75·qNet_control` and computes: a signed weighted distance from the current state to `Φ = 0` in a normalised (K⁺, log₂-exposure) space; the binding constraint by smallest normalised distance with a separate local-sensitivity ranking; and the minimum-cost action from a finite declared set of single actions (K⁺ correction, exposure reduction, permitted discontinuation) that restores a target margin — or an exhaustive finite-domain infeasibility result with a computational reason. A supporting auditor quantifies intervals over which the Tisdale score band is constant while Φ moves materially. A verification engine (16 gates, two tiers, plus nine negative controls) assigns every result `VERIFIED`, `UNVERIFIED` or `FAILED`, and `UNKNOWN` is never treated as a pass. Every number is traceable from DOI to parameter to computation to a reproducible result hash.
## 2. FINAL FEATURE LIST
Steady-state EP engine with convergence gates · Hill pore-block + declared combination rule with sensitivity variant · qNet / APD90 / RA biomarkers · internally calibrated Φ boundary · monotonicity scanning with multi-root handling · signed weighted margin (axis bisection + direction sampling + SLSQP refinement) with honest upper-bound labelling · computed binding constraint with critical values and alternative axis · exhaustive minimum-cost rescue over a declared finite action set · four-state infeasibility taxonomy with reason codes and closest-action shortfall · Tisdale blind-spot auditor with score-interval handling for unknown items · 16-gate two-tier verification with nine negative controls · credibility state on every result with mandated UI treatment · provenance + config/result hashing + JSON/PDF export · SQLite caching with warm starts gated by an equivalence check · nine local API endpoints · four-region scientific UI · fully offline operation · precomputed demo cache with live spot-verification.
## 3. FINAL EXCLUSIONS
Tissue/1D/2D/3D conduction, re-entry, spiral waves, whole heart · ECG/QT reconstruction · population of models · PBPK or any compartmental PK · large drug libraries (6 maximum) · ML/AI risk prediction · chatbot or any LLM in the compute path · EHR/PHI/real patient data · dosing output in clinical units · Mg²⁺ (D4) · extracellular Ca²⁺/Na⁺, temperature, pH, β-adrenergic tone · pacing CL as a margin axis (D3) · drug substitution search · multi-action rescue · epi/mid cell types · extra biomarkers (qInward, triangulation, APD50, CTD) · dynamic hERG binding · cloud, accounts, mobile app, microservices · any claim of clinical validation or TdP prediction.
## 4. FINAL DATA SOURCES
<table header-row="true">
<tr>
<td>Source</td>
<td>DOI / URL</td>
<td>Used for</td>
</tr>
<tr>
<td>O'Hara, Virág, Varró, Rudy 2011, PLoS Comput Biol 7(5):e1002061</td>
<td>10.1371/journal.pcbi.1002061</td>
<td>base physiology, control reference</td>
</tr>
<tr>
<td>Dutta et al. 2017, Front Physiol 8:616</td>
<td>10.3389/fphys.2017.00616</td>
<td>optimised conductances, qNet definition, CL 2000 ms protocol</td>
</tr>
<tr>
<td>Li et al. 2017, Circ Arrhythm Electrophysiol 10:e004628</td>
<td>10.1161/CIRCEP.116.004628</td>
<td>CiPA v1.0 model provenance (dynamic binding disabled, D1); IC50 table reproduction</td>
</tr>
<tr>
<td>Li et al. 2019, Clin Pharmacol Ther 105:466–475</td>
<td>10.1002/cpt.1184</td>
<td>qNet threshold reference band (non-comparable), free C_max, prior-art labels</td>
</tr>
<tr>
<td>Crumb et al. 2016, J Pharmacol Toxicol Methods 81:251–262</td>
<td>10.1016/j.vascn.2016.03.009</td>
<td>multichannel IC50 / Hill parameters</td>
</tr>
<tr>
<td>Tisdale et al. 2013, Circ Cardiovasc Qual Outcomes 6:479–487</td>
<td>10.1161/CIRCOUTCOMES.113.000152</td>
<td>clinical score for the blind-spot audit</td>
</tr>
<tr>
<td>Physiome exposure `ohara_rudy_cipa_v1_2017.cellml`</td>
<td>https://models.cellml.org/e/5a0</td>
<td>the model artefact itself</td>
</tr>
<tr>
<td>FDA/CiPA reference C implementation (GPL-3.0)</td>
<td>https://github.com/FDA/CiPA</td>
<td>independent numerical reference; **code not copied**</td>
</tr>
<tr>
<td>Myokit</td>
<td>https://myokit.org</td>
<td>ODE runtime, CellML import, fallback `ord-2011.mmt`</td>
</tr>
<tr>
<td>CredibleMeds</td>
<td>—</td>
<td>optional user-entered risk class; **nothing redistributed**</td>
</tr>
</table>
## 5. FINAL VALIDATION BATTERY
Gates **V-1** model integrity · **V-2** steady state · **V-3** units/ranges · **V-4** quadrature · **V-5** provenance · **V-6** control APD90 · **V-7** control qNet · **V-8** tolerance/timestep · **V-9** independent solver · **V-10** warm-start equivalence · **V-11** known-drug direction · **V-12** prior-art ordering · **V-13** K⁺ directionality · **V-14** stimulus sensitivity (advisory) · **V-15** RA reproducibility (advisory) · **V-16** negative controls behave.<br>Experiments **E1** control reproduction · **E2** known drug response · **E3** prior-art ordering · **E4** K⁺ directionality · **E5** numerical sensitivity · **E6** margin consistency · **E7** rescue consistency · **E8** infeasibility behaviour · **E9** clinical-score blind spot.<br>Negative controls **N-1** loose solver · **N-2** insufficient pacing · **N-3** out-of-domain exposure · **N-4** malformed drug data · **N-5** corrupted model · **N-6** unrecorded references · **N-7** non-credible action evaluation · **N-8** artefactual EAD · **N-9** non-monotone Φ.<br>Aggregation: any mandatory `FAIL` → `FAILED`; any mandatory `UNKNOWN` or downgrade tag → `UNVERIFIED`; all mandatory `PASS` and no tags → `VERIFIED`.
## 6. FINAL REPOSITORY TREE
As specified in §27 — `configs/`, `models/` (+ `vendor/`, `generated/`), `data/` (+ `scores/`, `scenarios/`), `backend/app/` (`schemas/`, `data/`, `ep/`, `engines/`, `services/`, `copy/`), `frontend/src/` (+ `tests/`), `validation/` (+ `battery_results/`, `golden/`), `scripts/`, `tests/` (`unit/`, `numerics/`, `integration/`, `api/`, `validation/`, `failure/`, `repro/`, `contract/`), `docs/`, `cache/` (+ `demo/`), `logs/`, `reports/`.
## 7. FINAL API LIST
`GET /health` · `GET /drugs` · `GET /scenarios` · `GET /validation` · `POST /simulate` · `POST /margin` · `POST /rescue` · `POST /blindspot` · `POST /verify` · `POST /report` — all under `http://127.0.0.1:8000/api/v1`, all returning `provenance`, `credibility`, `disclaimers`, `config_hash`, `result_hash`, with the budgets and error codes of §19.4 and §20.
## 8. FINAL UI SCREEN MAP
**HEADER:** product name, subtitle, model id + hash, config hash, OFFLINE badge, credibility chip, non-dismissible `DISC_GLOBAL`.<br>**LEFT:** scenario selector with `synthetic` badge, up to four drugs with log₂ exposure sliders, K⁺ slider, CL slider (greyed for margin with the `CL_EXCLUDED_PROTOCOL_BOUND` tooltip), Simulate and Margin buttons.<br>**CENTER (4 tabs):** action potential + I_net with the shaded qNet area · qNet/APD90 vs swept variable with the boundary line and crossing point · Φ curves per axis with roots marked · rescue table of all `|A|` rows.<br>**RIGHT:** safety margin (signed, unit convention, `≤` when sampled, status chip) · binding constraint with critical value and alternative axis · rescue button with best-action or infeasibility card · `DISC_MARGIN`.<br>**BOTTOM (4 tabs):** MECHANISM (per-channel block with IC50/Hill/DOI and per-current charge attribution) · CLINICAL-SCORE COMPARISON (band vs margin, insensitivity intervals, §13.4 verdict) · VERIFICATION (V-1..V-16 with observed vs threshold) · PROVENANCE (SOURCE → PARAMETER → COMPUTATION → OUTPUT, hashes, assumption IDs, export buttons).
## 9. FINAL 7-DAY PLAN
**Day 1** repo + model converted + transcription started (CP1: model runs). **Day 2** steady state + biomarkers + schema freeze + parameters `VERIFIED` (CP2: `/simulate` real). **Day 3** Φ + boundary + margin + binding (CP3: margin for DEMO-A). **Day 4** rescue + infeasibility + blind spot (CP4: feasible on DEMO-A, `INFEASIBLE_EXHAUSTIVE` on DEMO-B). **Day 5** verification wired + battery run + report (CP5: **FEATURE FREEZE**). **Day 6** demo cache + full green suite + rehearsals (CP6: 3-minute offline run within latency ceilings). **Day 7** freeze tag, offline rehearsal, backup machine and static fallback artefacts (CP7: signed-off freeze). No scope expansion after CP5.
## 10. FINAL DEMO SCRIPT
1. Load DEMO-A, Simulate → AP trace, qNet, APD90, boundary, `VERIFIED` (cached). 2. Margin → `+1.8` normalised units with the unit convention (cached). 3. Judge lowers K⁺ 4.5 → 3.8 on the precomputed grid → margin shrinks. 4. Continue to 3.7 → margin `+0.3`, approaching the boundary. 5. K⁺ 3.6 → Φ \< 0, unsafe side, crossing point annotated. 6. SCORE tab → Tisdale band constant across the interval while the margin crosses; §13.4 verdict. 7. VERIFICATION tab → all gates pass; then show the loose-solver entry being refused as `FAILED`. 8. MECHANISM tab → per-channel block with DOIs and per-current charge attribution. 9. Run Rescue (live, ≤ 8 s) → all 15 actions with cost/Φ/feasibility/credibility. 10. Best action card → minimum-cost K⁺ correction with post-rescue margin and `DISC_RESCUE`. 11. Load DEMO-B → `INFEASIBLE_EXHAUSTIVE` with reason `K_CEILING_BINDING`, closest action, shortfall, `DISC_INFEAS`. 12. Export JSON + PDF → provenance chain and identical `result_hash` on re-import. Total 3:00, offline, latency ceilings per §22.3.
## 11. FINAL JUDGE-Q&A
The sixteen questions and their approved answers are §31, mirrored verbatim into `docs/JUDGE_QA.md`. Core lines to memorise: *the cell model is prior art and cited; the novelty is the inverse layer; the margin is a distance, not a probability; a single cell cannot predict TdP; EAD is annotation, never definition; pharmacology numbers are human-transcribed with DOIs; the combination rule is a labelled assumption with a sensitivity check; "certificate" applies only to exhaustive finite-domain infeasibility; the clinical score is insensitive over an interval, not wrong; no LLM is in the compute path; this is not clinical advice.*
## 12. FINAL "DO NOT CHANGE THIS ARCHITECTURE" CONTRACT
1. Use the vendored ORd-CiPA v1.0 artefact with hash verification and the dynamic hERG binding disabled. Do not re-implement, re-derive or silently substitute physiology; the only legal fallback is `ORd2011-endo` with a documented trigger and a persistent banner.
2. Φ is defined on qNet against an internally calibrated boundary `rho·qNet_control`. Published CiPA thresholds are reference-only and are code-blocked from serving as the boundary.
3. EAD/RA may annotate and may downgrade credibility. It may never define the margin.
4. The margin is a signed weighted distance in the declared normalised state space, always accompanied by the unit convention and the "not a probability of clinical harm" caption, and labelled `≤` whenever it comes from direction sampling.
5. The binding constraint is computed by smallest normalised distance, never by inspection; local sensitivity is reported separately.
6. Rescue is an exhaustive enumeration of a finite declared single-action set with a declared cost ordering; the full evaluated table is always returned.
7. The four-state infeasibility taxonomy is mandatory, and the word "certificate" is reserved for `INFEASIBLE_EXHAUSTIVE`.
8. The clinical-score comparison reports insensitivity intervals only; the score is never called wrong and is never tuned.
9. Every result carries `VERIFIED` / `UNVERIFIED` / `FAILED`. `UNKNOWN` is never a pass. Negative controls must be able to fail the system.
10. No LLM in the compute path; no network at runtime; no patient data; no clinical units; no forbidden claim language; every important number hash-reproducible.
11. Scope is frozen at feature freeze (CP5). Additions belong in v2, recorded and rejected in the Deviation Register.
12. This document is the single source of truth. Implement it. Record any genuine contradiction as a deviation, then implement the recorded resolution.
