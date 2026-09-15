# Claims (§25)

## What we CAN claim (approved sentences — use verbatim)

1. "TorsadeTwin computes, for a declared modelled state, the distance to a model-defined repolarization-risk boundary defined on qNet in a published human ventricular myocyte model."
2. "It identifies which modelled variable reaches that boundary first within declared bounds."
3. "It exhaustively searches a declared finite set of permitted single actions for the minimum-cost action that restores a declared target margin, and reports when no element of that set does."
4. "It attaches a numerical credibility state to every result and refuses to present results that fail its verification gates as verified."
5. "Every number is traceable to a cited source, a model artefact hash, a solver configuration and a reproducible result hash."
6. "The system reproduces the qualitative direction and ordering expected from published in-silico cardiac safety work for the drugs and conditions tested (see §16)."
7. "This is a mechanistic computational research prototype for hypothesis generation and methodology demonstration."

## What we CANNOT claim (forbidden — in speech, slides, UI, code and README)

The canonical prohibited-language list is defined in `backend/app/copy/disclaimers.py` and enforced repository-wide by the copy test. Do not reproduce its entries, including as quoted examples.

## Note on the product name

"Twin" refers to a **cell-level mechanistic model twin of a declared synthetic state**, not a patient digital twin. The UI subtitle and README state this explicitly.

## Preferred framing vocabulary

mechanistic simulation · in-silico research prototype · model-defined safety margin · model-defined boundary · declared finite action set · exhaustive-domain infeasibility · hypothesis generation · reproducible in-silico analysis · numerical credibility gate · not a clinical decision-making device.

## Enforcement

`test_copy_forbidden_phrases.py` scans `backend/`, `frontend/src/`, `docs/`, `README.md` and `docs/DEMO_SCRIPT.md` for the forbidden list (case-insensitive, whitespace-normalised) and fails CI on any match. The disclaimer bar is non-dismissible in the DOM (asserted by a frontend test).
