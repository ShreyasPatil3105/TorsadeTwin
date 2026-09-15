# Frozen user-facing strings — single source of truth (§1.9, §25).
# Mirrored by frontend/src/copy/strings.ts; test_copy_parity asserts equality.

DISCLAIMERS = {
    "DISC_GLOBAL": "Research prototype. In-silico model output only. Not clinically validated. Not for clinical decision-making.",
    "DISC_MARGIN": "Margin = weighted distance in modelled-state space to the model-defined qNet boundary. It is NOT a probability of clinical harm.",
    "DISC_RESCUE": "Rescue = minimum-cost element of a declared finite action set that restores the target margin **in this model**. It is not a treatment recommendation.",
    "DISC_INFEAS": "Exhaustive over the declared finite action set only. Says nothing about actions outside that set.",
    "DISC_SCORE": "Comparison shows the score's insensitivity to a modelled variable over an interval. It does not establish that the score is incorrect.",
    "DISC_UNVERIFIED": "NOT TRUSTWORTHY — numerical credibility checks did not pass. Result shown for debugging only.",
}

# §1.8 research/demo framing (must appear on first screen)
RESEARCH_FRAMING = (
    "TorsadeTwin is an in-silico research prototype built on published cardiac electrophysiology "
    "and published ion-channel pharmacology. It computes distances to a **model-defined** "
    "repolarization-risk boundary. It does not predict Torsade de Pointes in any individual, "
    "has not been clinically validated, and must not be used for clinical decision-making."
)

# §9.6 margin UI phrasing
MARGIN_HEADLINE = "Safety margin (model-defined): {value} normalised units"
MARGIN_SUBLINE = (
    "= {value} mM of K+ equivalent, or {value} doublings of exposure equivalent, "
    "to reach the model-defined qNet boundary."
)
MARGIN_CAPTION = "This is a distance in modelled-state space. It is NOT a probability of clinical harm."
MARGIN_UNSAFE_SIDE = "Current state is on the unsafe side of the model-defined boundary; distance back to the boundary = {value} units."

# §11.2 rescue target phrasing
RESCUE_TARGET_LABEL = "target margin: qNet at least 5% of control above the model-defined boundary"

# §12.2 infeasibility status -> permitted user-facing wording (the ONLY path to these strings)
INFEASIBILITY_WORDING = {
    "FEASIBLE": "Minimum-cost permitted single action found.",
    "INFEASIBLE_EXHAUSTIVE": (
        "Certificate of infeasibility over the declared finite action set: "
        "no permitted single action restores the target margin."
    ),
    "NO_SOLUTION_FOUND": (
        "No feasible single intervention found within the defined search domain "
        "(one or more results are within numerical tolerance of the target)."
    ),
    "INCOMPLETE_SEARCH": "Search incomplete — feasibility unknown. N of M actions could not be credibly evaluated.",
}

# §13.4 blind-spot verdict template
BLINDSPOT_VERDICT_TEMPLATE = (
    "Over {var} = {hi} -> {lo} the Tisdale band remains **{band}** "
    "(score interval unchanged at [{smin}, {smax}]) because its potassium item is a threshold at <= 3.5 mM, "
    "while the mechanistic margin in this model falls from +{m_hi} to {m_lo} normalised units and "
    "crosses the model-defined boundary at {var} = {crossing} mM. The score is **insensitive to this "
    "modelled variable over this interval**; this comparison does not establish that the score is incorrect."
)

# §25.2 forbidden phrases (case-insensitive, whitespace-normalised grep across the repo)
FORBIDDEN_PHRASES = [
    "will have TdP",
    "torsadogenic patient",
    "predicts arrhythmia",
    "clinically unsafe",
    "safe to prescribe",
    "predicts TdP in patients",
    "clinically validated",
    "guarantees safety",
    "recommends treatment",
    "proves the patient is safe",
    "personalised medicine",
    "digital twin of a patient",
    "replaces clinical judgement",
    "FDA-compliant",
    "CiPA-validated",
    "detects arrhythmia",
    "our model is more accurate than clinical scores",
    "proves the score is wrong",
    "probability of arrhythmia",
    "risk percentage",
    "the score is wrong",
    "Tisdale fails",
    "score missed the risk",
    "our model is better",
    "no treatment exists",
    "nothing can be done",
    "clinically untreatable",
]

# §12.2 forbidden strings except for INFEASIBLE_EXHAUSTIVE
INFEASIBILITY_FORBIDDEN_UNLESS_EXHAUSTIVE = ["proved", "certificate", "impossible", "guaranteed"]

# §25.1 approved claim sentences (verbatim)
APPROVED_CLAIMS = [
    "TorsadeTwin computes, for a declared modelled state, the distance to a model-defined repolarization-risk boundary defined on qNet in a published human ventricular myocyte model.",
    "It identifies which modelled variable reaches that boundary first within declared bounds.",
    "It exhaustively searches a declared finite set of permitted single actions for the minimum-cost action that restores a declared target margin, and reports when no element of that set does.",
    "It attaches a numerical credibility state to every result and refuses to present results that fail its verification gates as verified.",
    "Every number is traceable to a cited source, a model artefact hash, a solver configuration and a reproducible result hash.",
    "The system reproduces the qualitative direction and ordering expected from published in-silico cardiac safety work for the drugs and conditions tested (see §16).",
    "This is a mechanistic computational research prototype for hypothesis generation and methodology demonstration.",
]

# §7.2 excluded physiological variables -> reason strings (display verbatim)
EXCLUDED_VARIABLES = {
    "Mg2+": "NOT MODELLED",
    "Mg2+_reason": "The selected model contains no Mg2+-dependent conductance or Mg2+ block term, and no published Mg2+ dose-response is calibrated for it. Including it would require inventing physiology.",
    "Ca2+_extracellular": "NOT SETTABLE in v1.0",
    "Ca2+_extracellular_reason": "Changing extracellular Ca2+ perturbs Ca-handling calibration; out of scope for v1.0.",
    "Na+_extracellular": "NOT SETTABLE in v1.0",
    "Na+_extracellular_reason": "No demo-relevant pathway; out of scope.",
    "temperature_pH_beta_sex_celltype": "NOT MODELLED in v1.0",
    "temperature_pH_beta_sex_celltype_reason": "No calibrated pathway in the selected model artefact for v1.0.",
}
