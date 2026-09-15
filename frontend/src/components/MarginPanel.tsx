import React from "react";
import { useStore } from "../state/store";
import { UNIT_CONVENTION, MARGIN_CAPTION } from "../copy/strings";

export function MarginPanel() {
  const store = useStore();
  const m = store.margin;
  if (!m) return <div className="panel"><h3>Safety margin</h3><p className="muted">Run a margin computation.</p></div>;

  const signed = m.m_signed;
  const prefix = m.m_status === "SAMPLED_UB" ? "≤ " : "";
  const display = signed === null ? "—" : `${prefix}${signed.toFixed(2)}`;

  return (
    <div className="panel">
      <h3>Safety margin (model-defined)</h3>
      <div className="margin-number mono" data-testid="margin-number">
        {signed !== null && signed < 0 ? "−" : ""}
        {display} normalised units
      </div>
      <div className="caption">{UNIT_CONVENTION}</div>
      <div className="status-chip">{m.m_status}</div>
      <div className="caption">{MARGIN_CAPTION}</div>
    </div>
  );
}
