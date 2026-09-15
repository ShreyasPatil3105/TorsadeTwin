import React from "react";
import { useStore } from "../state/store";

export function BindingPanel() {
  const store = useStore();
  const b = store.margin?.binding_constraint;
  if (!b) return <div className="panel"><h3>Binding constraint</h3><p className="muted">—</p></div>;

  return (
    <div className="panel">
      <h3>Binding constraint</h3>
      {b.axis ? (
        <>
          <div className="mono">
            {b.axis} — critical {b.critical_raw_value?.toFixed(2)}
          </div>
          {b.alternative_axis && (
            <div className="muted">alternative: {b.alternative_axis} @ {b.alternative_critical_value?.toFixed(2)}</div>
          )}
          {b.distance_vs_sensitivity_disagree && (
            <div className="badge" title="The most influential variable locally is not the nearest boundary; distance defines the binding constraint.">
              DISTANCE != SENSITIVITY
            </div>
          )}
        </>
      ) : (
        <div className="muted">No reachable boundary in box.</div>
      )}
    </div>
  );
}
