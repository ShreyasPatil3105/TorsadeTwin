# Deviation Register (§0.3)

Frozen resolutions from the Chief Scientist that the implementer MUST honour. Any new deviation discovered during implementation must be recorded here with tension, resolution and consequence — then implemented. Silent deviation is a build failure.

| ID | Tension found | Frozen resolution | Consequence the implementer must honour |
|---|---|---|---|
| D1 | Simple pore-block (Hill) vs dynamic hERG binding used for CiPA qNet thresholds | MVP uses Hill/pore block on all channels including IKr; dynamic drug-hERG binding pathway disabled (drug concentration held at 0) | Absolute qNet values are NOT numerically comparable to published CiPA thresholds; risk boundary is internally calibrated to the model's own drug-free control (§8.4); published thresholds shown only as a reference band labelled LITERATURE_REFERENCE_NOT_COMPARABLE |
| D2 | EAD detection requested, but EAD must not define the margin | Φ is defined purely on qNet; RA detection is a boolean annotation with its own credibility flag, can only downgrade trust | No code path may compute the margin from RA |
| D3 | Pacing cycle length as a possible margin variable; qNet is protocol-defined at CL=2000 ms | CL is a settable input (affects APD90/trace) but excluded from margin/rescue axes in v1.0 | UI greys out CL as a margin axis and shows CL_EXCLUDED_PROTOCOL_BOUND |
| D4 | Mg2+ requested | Excluded — no Mg2+-dependent conductance/block term in the selected model, no published Mg2+ dose-response calibrated | UI shows Mg2+ as NOT MODELLED; no hidden Mg2+ parameter may exist in code or config |
| D5 | "Patient state" without fake clinical data | All scenarios are synthetic, declared, non-identifiable regimen states (data/scenarios/*.yaml with synthetic: true) | The word "patient" in the UI is always rendered as "scenario" or "modelled state" |
| D6 | Combination pharmacology is scientifically uncertain | Independent, non-competitive block per channel; fractional-block multiplication across drugs (COMBO_RULE_INDEP_MULT_v1); additive-occupancy sensitivity variant reported | Never present the combination rule as validated; report contains the assumption ID and its sensitivity delta |

## Newly recorded deviations during implementation

None. All implementation decisions fell within the frozen contract. Any future deviation must be appended below with a written justification.
