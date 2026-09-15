import React from "react";
import { useStore } from "../state/store";

export function VerificationTable() {
  const store = useStore();
  const v = store.verify;
  if (!v) return <div className="panel"><h3>Verification — V-1..V-16</h3><p className="muted">Run /verify to populate.</p></div>;

  return (
    <div className="panel">
      <h3>Verification — checks</h3>
      <table>
        <thead>
          <tr><th>id</th><th>check</th><th>tier</th><th>state</th></tr>
        </thead>
        <tbody>
          {v.checks.map((c) => (
            <tr key={c.id}>
              <td className="mono">{c.id}</td>
              <td>{c.name}</td>
              <td>{c.tier}</td>
              <td className={`mono state-${c.state.toLowerCase()}`}>{c.state}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="status-chip">aggregate: {v.aggregate}</div>
    </div>
  );
}
