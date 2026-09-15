// Frontend copy mirrors the backend frozen strings used by the main UI.
// Keep changes synchronized with backend/app/copy/disclaimers.py.
export const COPY = Object.freeze({
  DISC_GLOBAL: "Research prototype. In-silico model output only. Not clinically validated. Not for clinical decision-making.",
  DISC_MARGIN: "Margin = weighted distance in modelled-state space to the model-defined qNet boundary. It is NOT a probability of clinical harm.",
  DISC_RESCUE: "Rescue = minimum-cost element of a declared finite action set that restores the target margin **in this model**. It is not a treatment recommendation.",
  DISC_INFEAS: "Exhaustive over the declared finite action set only. Says nothing about actions outside that set.",
  DISC_SCORE: "Comparison shows the score's insensitivity to a modelled variable over an interval. It does not establish that the score is incorrect.",
  DISC_UNVERIFIED: "NOT TRUSTWORTHY — numerical credibility checks did not pass. Result shown for debugging only."
});
