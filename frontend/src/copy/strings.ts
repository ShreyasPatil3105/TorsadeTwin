// Frozen user-facing strings — mirror of backend/app/copy/disclaimers.py (§21.5 copy parity).
export const DISCLAIMERS: Record<string, string> = {
  DISC_GLOBAL:
    "Research prototype. In-silico model output only. Not clinically validated. Not for clinical decision-making.",
  DISC_MARGIN:
    "Margin = weighted distance in modelled-state space to the model-defined qNet boundary. It is NOT a probability of clinical harm.",
  DISC_RESCUE:
    "Rescue = minimum-cost element of a declared finite action set that restores the target margin **in this model**. It is not a treatment recommendation.",
  DISC_INFEAS:
    "Exhaustive over the declared finite action set only. Says nothing about actions outside that set.",
  DISC_SCORE:
    "Comparison shows the score's insensitivity to a modelled variable over an interval. It does not establish that the score is incorrect.",
  DISC_UNVERIFIED:
    "NOT TRUSTWORTHY — numerical credibility checks did not pass. Result shown for debugging only.",
};

export const RESEARCH_FRAMING =
  "TorsadeTwin is an in-silico research prototype built on published cardiac electrophysiology and published ion-channel pharmacology. It computes distances to a **model-defined** repolarization-risk boundary. It does not predict Torsade de Pointes in any individual, has no clinical-validation evidence, and must not be used for clinical decision-making.";

export const MARGIN_CAPTION =
  "This is a distance in modelled-state space. It is NOT a probability of clinical harm.";

export const UNIT_CONVENTION =
  "1 normalised unit = 1 mM K+ = one doubling of exposure";

export const CL_EXCLUDED_TOOLTIP =
  "CL_EXCLUDED_PROTOCOL_BOUND — pacing cycle length is excluded from the margin/rescue axes in v1.0 (deviation D3).";

export const MG2_NOT_MODELLED =
  "Mg2+ — NOT MODELLED. The selected model contains no Mg2+-dependent conductance or Mg2+ block term, and no published Mg2+ dose-response is calibrated for it. Including it would require inventing physiology.";

export const INFEASIBILITY_WORDING: Record<string, string> = {
  FEASIBLE: "Minimum-cost permitted single action found.",
  INFEASIBLE_EXHAUSTIVE:
    "Certificate of infeasibility over the declared finite action set: no permitted single action restores the target margin.",
  NO_SOLUTION_FOUND:
    "No feasible single intervention found within the defined search domain (one or more results are within numerical tolerance of the target).",
  INCOMPLETE_SEARCH:
    "Search incomplete — feasibility unknown. N of M actions could not be credibly evaluated.",
};
