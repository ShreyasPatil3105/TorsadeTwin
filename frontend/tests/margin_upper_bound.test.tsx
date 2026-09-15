import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MarginPanel } from "../src/components/MarginPanel";
import { useStore } from "../src/state/store";

describe("margin upper bound", () => {
  it("shows <= prefix when m_status = SAMPLED_UB", () => {
    useStore.setState({
      margin: {
        phi_now: 0.004,
        m_signed: 1.83,
        m_status: "SAMPLED_UB",
        m_label: "upper bound on the true minimum weighted distance",
        axes: [],
        binding_constraint: { axis: "k_o_mM", critical_raw_value: 3.42, tied_axes: [], alternative_axis: null, alternative_critical_value: null, distance_vs_sensitivity_disagree: false },
        n_phi_evals: 41,
        unit_convention: "1 normalised unit = 1 mM K+ = one doubling of exposure",
        credibility: { state: "VERIFIED" },
        disclaimers: [],
      },
    });
    render(<MarginPanel />);
    expect(screen.getByTestId("margin-number").textContent).toContain("≤");
  });

  it("shows no <= prefix for EXACT_AXIS", () => {
    useStore.setState({
      margin: {
        phi_now: 0.004,
        m_signed: 1.83,
        m_status: "EXACT_AXIS",
        m_label: "exact along a single axis",
        axes: [],
        binding_constraint: { axis: "k_o_mM", critical_raw_value: 3.42, tied_axes: [], alternative_axis: null, alternative_critical_value: null, distance_vs_sensitivity_disagree: false },
        n_phi_evals: 10,
        unit_convention: "1 normalised unit = 1 mM K+ = one doubling of exposure",
        credibility: { state: "VERIFIED" },
        disclaimers: [],
      },
    });
    render(<MarginPanel />);
    expect(screen.getByTestId("margin-number").textContent).not.toContain("≤");
  });
});
