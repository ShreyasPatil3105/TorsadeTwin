import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const FORBIDDEN = [
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
  "probability of arrhythmia",
  "risk percentage",
  "the score is wrong",
  "Tisdale fails",
  "score missed the risk",
  "our model is better",
  "no treatment exists",
  "nothing can be done",
  "clinically untreatable",
];

const normalize = (s: string) => s.toLowerCase().replace(/\s+/g, " ");

describe("no forbidden phrases", () => {
  it("frontend source contains no forbidden claim language", () => {
    const srcDir = resolve(__dirname, "../src");
    const { readdirSync, statSync } = require("node:fs");
    const walk = (dir: string): string[] =>
      readdirSync(dir).flatMap((f: string) => {
        const p = resolve(dir, f);
        return statSync(p).isDirectory() ? walk(p) : [p];
      });
    const files = walk(srcDir).filter((f) => /\.(ts|tsx|css)$/.test(f));
    for (const f of files) {
      const text = normalize(readFileSync(f, "utf-8"));
      for (const phrase of FORBIDDEN) {
        expect(text.includes(normalize(phrase))).toBe(false);
      }
    }
  });
});
