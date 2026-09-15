# L7 — Rescue engine (§11) + infeasibility classification (§12). Core novelty, part 2.
# Exhaustive enumeration of a DECLARED FINITE single-action set; minimum-cost feasible action;
# four-state infeasibility taxonomy. No gradient search, no heuristics, no early exit.
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..schemas.common import StateSpec, DrugExposure
from .phi import PhiEval
from .margin import compute_margin


@dataclass(frozen=True)
class Action:
    class_: str
    param: dict
    cost: float

    def label(self) -> str:
        if self.class_ == "A0_NO_ACTION":
            return "A0_NO_ACTION"
        if self.class_ == "A1_K_CORRECTION":
            return f"A1_K_CORRECTION(k_o={self.param['k_o_mM']})"
        if self.class_ == "A2_EXPOSURE_REDUCTION":
            return f"A2_EXPOSURE_REDUCTION({self.param['drug']} x{self.param['factor']})"
        if self.class_ == "A3_DISCONTINUATION":
            return f"A3_DISCONTINUATION({self.param['drug']})"
        return self.class_


@dataclass(frozen=True)
class EvaluatedAction:
    action: Action
    phi: float | None
    feasible: bool
    credibility: str
    skipped_out_of_box: bool = False


@dataclass(frozen=True)
class InfeasibilityReport:
    reason_code: str
    explanation: str
    closest_action: dict
    shortfall_normalised: float | None = None
    limiting_bound: str = ""
    what_would_help: str = "Two-action combinations and drug substitution are outside the declared search scope."


@dataclass(frozen=True)
class RescueResult:
    status: str
    phi_target: float
    best_action: Action | None
    co_optimal: list[Action]
    evaluated: list[EvaluatedAction]
    action_set_size: int
    n_noncredible: int
    infeasibility: InfeasibilityReport | None = None
    post_margin: float | None = None
    post_phi: float | None = None


class RescueEngine:
    def __init__(self, rescue_cfg: dict, registry):
        self.cfg = rescue_cfg
        self.registry = registry

    def build_action_set(self, x0: StateSpec) -> list[Action]:
        """§11.3. Deterministic enumeration order."""
        actions: list[Action] = []
        actions.append(Action("A0_NO_ACTION", {}, 0.0))
        k0 = x0.k_o_mM
        for kt in self.cfg["action"]["k_correction_targets_mM"]:
            if kt > k0 and kt <= self.cfg["action"]["k_ceiling_mM"]:
                cost = self.cfg["cost_weights"]["w_K"] * (kt - k0) / 1.0
                actions.append(Action("A1_K_CORRECTION", {"k_o_mM": kt}, cost))
        for d in x0.drugs:
            if d.exposure_multiplier > 0:
                for factor in self.cfg["action"]["exposure_reduction_factors"]:
                    cost = self.cfg["cost_weights"]["w_E"] * abs(
                        __import__("math").log2(factor))
                    actions.append(Action("A2_EXPOSURE_REDUCTION", {"drug": d.drug_id, "factor": factor}, cost))
                rec = self.registry.get(d.drug_id)
                if rec.discontinuable:
                    actions.append(Action("A3_DISCONTINUATION", {"drug": d.drug_id},
                                          self.cfg["cost_weights"]["w_D"]))
        return actions

    def run(self, phi: Callable[[StateSpec], PhiEval], x0: StateSpec, tau: float,
            qnet_ctrl: float, cost_weights: dict | None = None, allow_discontinuation: bool = True,
            compute_post_margin: bool = True, margin_cfg: dict | None = None) -> RescueResult:
        if cost_weights:
            self.cfg["cost_weights"].update(cost_weights)
        if not allow_discontinuation:
            self.cfg["cost_weights"]["w_D"] = float("inf")
        phi_target = tau * qnet_ctrl
        actions = self.build_action_set(x0)
        if len(actions) > self.cfg["action"]["max_action_set_size"]:
            from ..services.errors import TorsadeTwinError

            raise TorsadeTwinError("E_ACTION_SET_TOO_LARGE", "Declared action set exceeds the permitted size.", http_status=500)
        evaluated: list[EvaluatedAction] = []
        for a in actions:
            x_a = self._apply(x0, a)
            res = phi(x_a)
            feasible = res.credibility == "VERIFIED" and res.phi is not None and res.phi >= phi_target
            evaluated.append(EvaluatedAction(action=a, phi=res.phi, feasible=feasible,
                                             credibility=res.credibility))
        n_noncredible = sum(1 for e in evaluated if e.credibility != "VERIFIED")
        feasible_credible = [e for e in evaluated if e.feasible and e.credibility == "VERIFIED"]
        if feasible_credible:
            min_cost = min(e.action.cost for e in feasible_credible)
            best = [e for e in feasible_credible if abs(e.action.cost - min_cost) <= self.cfg["tol_cost"]]
            best_sorted = sorted(best, key=lambda e: (e.action.class_, str(e.action.param)))
            chosen = best_sorted[0]
            co_optimal = [e.action for e in best_sorted[1:]]
            post_phi = chosen.phi
            post_margin = None
            if compute_post_margin and margin_cfg:
                mr = compute_margin(phi, self._apply(x0, chosen.action), self._axes(x0), margin_cfg)
                post_margin = mr.m_signed
            return RescueResult(status="FEASIBLE", phi_target=phi_target, best_action=chosen.action,
                                co_optimal=co_optimal, evaluated=evaluated, action_set_size=len(actions),
                                n_noncredible=n_noncredible, post_margin=post_margin, post_phi=post_phi)
        # no credible feasible action -> classify
        tol = self.cfg["tol_phi_borderline"]
        all_credible = n_noncredible == 0
        any_borderline = any(abs(e.phi - phi_target) <= tol for e in evaluated
                             if e.credibility == "VERIFIED" and e.phi is not None)
        if not all_credible:
            status = "INCOMPLETE_SEARCH"
        elif any_borderline:
            status = "NO_SOLUTION_FOUND"
        else:
            status = "INFEASIBLE_EXHAUSTIVE"
        inf = self._infeasibility_report(evaluated, phi_target, status)
        return RescueResult(status=status, phi_target=phi_target, best_action=None, co_optimal=[],
                            evaluated=evaluated, action_set_size=len(actions), n_noncredible=n_noncredible,
                            infeasibility=inf)

    def _apply(self, x0: StateSpec, a: Action) -> StateSpec:
        drugs = {d.drug_id: d.exposure_multiplier for d in x0.drugs}
        k = x0.k_o_mM
        if a.class_ == "A1_K_CORRECTION":
            k = a.param["k_o_mM"]
        elif a.class_ == "A2_EXPOSURE_REDUCTION":
            d = a.param["drug"]
            drugs[d] = drugs.get(d, 0.0) * a.param["factor"]
        elif a.class_ == "A3_DISCONTINUATION":
            drugs[a.param["drug"]] = 0.0
        return StateSpec(
            drugs=[DrugExposure(drug_id=d, exposure_multiplier=m) for d, m in drugs.items()],
            k_o_mM=k, cl_ms=x0.cl_ms, cell_type=x0.cell_type, solver_profile=x0.solver_profile,
            combo_rule=x0.combo_rule,
        )

    def _axes(self, x0: StateSpec) -> list[str]:
        axes = ["k_o_mM"]
        for d in x0.drugs:
            axes.append(f"exposure:{d.drug_id}")
        return axes

    def _infeasibility_report(self, evaluated: list[EvaluatedAction], phi_target: float,
                              status: str) -> InfeasibilityReport | None:
        if status not in ("INFEASIBLE_EXHAUSTIVE", "NO_SOLUTION_FOUND"):
            return None
        # closest action = the one with the smallest shortfall
        best = None
        best_short = None
        for e in evaluated:
            if e.credibility != "VERIFIED":
                continue
            if e.phi is None:
                continue
            short = phi_target - e.phi
            if best is None or short < best_short:
                best = e
                best_short = short
        k_actions = [e for e in evaluated if e.action.class_ == "A1_K_CORRECTION"]
        e_actions = [e for e in evaluated if e.action.class_ == "A2_EXPOSURE_REDUCTION"]
        d_actions = [e for e in evaluated if e.action.class_ == "A3_DISCONTINUATION"]
        reason = "MULTIPLE_BOUNDS_BINDING"
        limiting = ""
        credible_k = [e.phi for e in k_actions if e.credibility == "VERIFIED" and e.phi is not None]
        credible_e = [e.phi for e in e_actions if e.credibility == "VERIFIED" and e.phi is not None]
        if credible_k and max(credible_k) < phi_target:
            reason = "K_CEILING_BINDING"
            limiting = "A1 ceiling K_o <= 5.4 mM"
        elif credible_e and max(credible_e) < phi_target:
            reason = "EXPOSURE_FLOOR_BINDING"
            limiting = "A2 floor factor >= 0.25"
        elif not d_actions:
            reason = "DISCONTINUATION_NOT_PERMITTED"
            limiting = "A3 not permitted"
        explanation = (
            f"The largest permitted single action reaches Phi = {max((e.phi for e in evaluated if e.credibility == 'VERIFIED' and e.phi is not None), default=float('-inf')):.4f} C/F, "
            f"still below the target {phi_target:.4f} C/F. {limiting}."
        )
        return InfeasibilityReport(
            reason_code=reason,
            explanation=explanation,
            closest_action={"class": best.action.class_, "param": best.action.param, "phi": best.phi,
                            "shortfall": round(best_short, 4)},
            shortfall_normalised=round(best_short / max(abs(phi_target), 1e-12), 4),
            limiting_bound=limiting,
        )
