import { describe, expect, it } from "vitest";
import { UNIT_CONVENTION } from "../src/copy/strings";

describe("plot units", () => {
  it("unit convention is displayed verbatim", () => {
    expect(UNIT_CONVENTION).toBe("1 normalised unit = 1 mM K+ = one doubling of exposure");
  });
});
