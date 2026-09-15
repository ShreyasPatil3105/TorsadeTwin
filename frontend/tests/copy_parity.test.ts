import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { DISCLAIMERS } from "../src/copy/strings";

const backend = readFileSync(resolve(__dirname, "../../backend/app/copy/disclaimers.py"), "utf-8");

describe("copy parity", () => {
  it("frontend DISC_* strings equal backend values", () => {
    for (const [key, value] of Object.entries(DISCLAIMERS)) {
      expect(backend).toContain(key);
      expect(backend).toContain(value);
    }
  });
});
