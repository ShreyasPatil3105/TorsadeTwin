# Judge QA (§31) — hostile Q&A, mirrored verbatim

**1. Isn't this just CiPA?**
No — and we use CiPA as prior art deliberately. CiPA is a forward risk-assessment paradigm: given a drug at 1–4× C_max, compute qNet and classify the drug. We consume that machinery and add an inverse layer: given a *state* (drugs plus electrolytes), compute the distance to a model-defined boundary, the binding variable, and the minimum permitted single action that restores a target margin — or exhaustively show that no permitted single action does. CiPA does not ask or answer those questions.

**2. Isn't this just ApPredict?**
ApPredict/AP-Portal computes forward APD/qNet changes for drug-block inputs. It is a simulator front-end. We do not compete with its physiology; we wrap a constrained inverse solver, a declared finite action search with infeasibility classification, and a credibility gate around that class of forward engine.

**3. Isn't this just Myokit?**
Myokit is our ODE/CVODES runtime, like NumPy is a dependency. It is explicitly credited. It provides no margin, no binding-constraint identification, no rescue search, and no infeasibility semantics.

**4. Isn't this just Certara/Simcyp?**
Commercial platforms do forward cardiac safety simulation, often with PBPK, at far greater scope and validation. They are closed, licensed and not reproducible line-by-line. We claim neither their scope nor their validation. Our claim is a specific, open, reproducible inverse computation with explicit infeasibility semantics and a numerical credibility gate on every result.

**5. What exactly is novel?**
One sentence: the system-level composition of (a) a signed weighted-distance margin to a model-defined qNet boundary in a declared state space, (b) computed binding-constraint identification, (c) a minimum-cost search over a declared finite action set, (d) an explicit distinction between exhaustive finite-domain infeasibility and "no solution found", each result gated by a numerical credibility state. Every underlying component — ORd, qNet, Hill block, APD90, Tisdale — is prior art and is cited as such.

**6. Is your margin validated?**
No, and we never say it is. The *algorithm* is verified: it recovers closed-form distances on analytic surrogate functions, and its root-finding is reproducible to declared tolerances. The *clinical meaning* of the margin is unvalidated. It is a distance in modelled-state space, not a probability of harm. Validating it clinically would require outcome data we do not have and do not claim.

**7. Can a single cell predict TdP?**
No. Single-cell models cannot represent re-entry, tissue heterogeneity or conduction, and TdP is a tissue-level phenomenon. That is precisely why our functional is a *model-defined repolarization-risk boundary* on qNet, not a TdP prediction, and why every output carries that language and disclaimer.

**8. How do you know your EAD isn't a numerical artifact?**
We assume it might be. EAD/RA detection is deliberately **not** part of the margin definition — the margin is defined on the smooth qNet integral. Any RA flag must reproduce under the tight solver profile and a finer log grid, or it is labelled `ARTEFACT_SUSPECTED` and cannot appear as verified. Our negative-control suite deliberately manufactures an artefact under loose settings and requires the system to reject it.

**9. Where do IC50 values come from?**
Published multichannel manual-patch data (Crumb et al. 2016, doi:10.1016/j.vascn.2016.03.009), transcribed by a human, double-entered by a second team member, stored with DOI, table reference and a verification status. The API refuses to serve any parameter that is not `VERIFIED`. No values are generated, recalled or interpolated by a language model.

**10. What combination assumption are you making?**
Independent, non-competitive block with fractional effects multiplied per channel (`COMBO_RULE_INDEP_MULT_v1`). We label it an assumption, not a validated law, and we compute an additive-occupancy alternative for every result. If the two rules place the state on opposite sides of the boundary, the result's credibility is capped at `UNVERIFIED`.

**11. What happens outside the validated range?**
Inputs outside declared domains are rejected. Inputs inside the model domain but outside the calibrated band (for example exposure above 25× free C_max, or K+ outside 3.0–5.5 mM) are computed but permanently tagged `OUT_OF_CALIBRATED_RANGE` / `OUT_OF_PHYSIOLOGICAL_RANGE` and can never reach `VERIFIED`.

**12. Why should we trust the rescue action?**
Trust it only as a model statement. It says: within this model, this declared action set and this cost ordering, this is the cheapest single action whose recomputed Φ meets the target. We independently recompute the post-action state and its margin, we show the full evaluated table for every action, and we label the cost weights as a declared search preference rather than a clinical judgement. It is explicitly not a treatment recommendation.

**13. What does infeasibility actually mean?**
Exactly one thing: every element of a finite, declared, published-in-the-report action set was evaluated, all evaluations passed the credibility gate, and none reached the target margin. That is complete with respect to that set — not a proof about physiology, actions outside the set, or combinations of actions. If any evaluation is missing, non-credible or numerically borderline, we downgrade the wording to "no feasible single intervention found within the defined search domain", and the word *certificate* is removed by code, not by discipline.

**14. Why not just use Tisdale?**
Use it — it is validated for its purpose, and we compute it. Our point is narrower and measurable: it is an ordinal score with threshold items, so over K+ 4.5 → 3.6 mM its band can remain constant while a mechanistic quantity in this model moves substantially and crosses the model-defined boundary. We report that as *insensitivity of the score to a modelled variable over an interval*. We do not judge the score's correctness or claim clinical superiority for our margin.

**15. Why can't ChatGPT do this?**
Because the answer is the output of a stiff ODE solve iterated by a root-finder and an exhaustive search — roughly 40–300 steady-state simulations per query, each hash-reproducible to declared tolerances. A language model can neither integrate the ODEs nor guarantee the enumeration; and no LLM appears anywhere in our compute path.

**16. Are you giving clinical advice?**
No. There are no patient records, no doses in clinical units, no infusion rates, no recommendation verbs, and no clinical risk probabilities anywhere in the system. Scenarios are declared synthetic states. Every screen and export carries the frozen global research disclaimer defined in the copy module, and a CI test fails the build if prohibited claim language appears anywhere in the repository.

## Core lines to memorise

- The cell model is prior art and cited; the novelty is the inverse layer.
- The margin is a distance, not a probability.
- A single cell cannot predict TdP.
- EAD is annotation, never definition.
- Pharmacology numbers are human-transcribed with DOIs.
- The combination rule is a labelled assumption with a sensitivity check.
- "certificate" applies only to exhaustive finite-domain infeasibility.
- The clinical score is insensitive over an interval, not wrong.
- No LLM is in the compute path.
- This is not clinical advice.
