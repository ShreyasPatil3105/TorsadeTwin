import React from "react";
import { useStore } from "../state/store";

export function MechanismTable() {
  const store = useStore();
  const sim = store.simulate;
  if (!sim) return <div className="panel"><h3>Mechanism — per-channel block</h3><p className="muted">—</p></div>;

  return (
    <div className="panel">
      <h3>Per-channel block (fraction blocked) — IC50, Hill, DOI in the provenance panel</h3>
      <table>
        <thead>
          <tr><th>channel</th><th>block fraction</th></tr>
        </thead>
        <tbody>
          {Object.entries(sim.block).map(([ch, b]) => (
            <tr key={ch}>
              <td className="mono">{ch}</td>
              <td className="mono">{b.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
