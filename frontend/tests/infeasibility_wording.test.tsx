import { describe, expect, it } from "vitest";
import { INFEASIBILITY_WORDING } from "../src/copy/strings";

describe("infeasibility wording", () => {
  it("maps exactly the four statuses", () => {
    expect(Object.keys(INFEASIBILITY_WORDING).sort()).toEqual([
      "FEASIBLE",
      "INCOMPLETE_SEARCH",
      "INFEASIBLE_EXHAUSTIVE",
      "NO_SOLUTION_FOUND",
    ]);
  });

  it("certificate appears only for INFEASIBLE_EXHAUSTIVE", () => {
    for (const [status, wording] of Object.entries(INFEASIBILITY_WORDING)) {
      expect(wording.toLowerCase().includes("certificate")).toBe(status === "INFEASIBLE_EXHAUSTIVE");
    }
  });
});
