import React from "react";
import { DISCLAIMERS } from "../copy/strings";

export function ScoreComparison() {
  return (
    <div className="panel">
      <h3>Clinical-score comparison (Tisdale band vs mechanistic margin)</h3>
      <p className="muted">Run the blind-spot audit (/api/v1/blindspot) to populate the sweep, insensitivity intervals and the §13.4 verdict.</p>
      <div className="caption">{DISCLAIMERS.DISC_SCORE}</div>
    </div>
  );
}
