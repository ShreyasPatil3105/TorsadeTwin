import React from "react";
import { useStore } from "../state/store";
import { DISCLAIMERS, INFEASIBILITY_WORDING } from "../copy/strings";

export function RescuePanel({ compact }: { compact?: boolean }) {
  const store = useStore();
  const r = store.rescue;

  if (compact) {
    if (!r) return <div className="panel"><h3>Rescue</h3><p className="muted">Run the rescue solver.</p></div>;
    return (
      <div className="panel">
        <h3>Rescue</h3>
        {r.best_action ? (
          <div className="best-action-card" data-testid="best-action">
            <div className="mono">{r.best_action.class}</div>
            <div className="muted">cost {r.best_action.cost.toFixed(2)} · φ after {r.best_action.phi_after.toFixed(4)}</div>
            <div className="caption">{DISCLAIMERS.DISC_RESCUE}</div>
          </div>
        ) : (
          <div className="infeasibility-card" data-testid="infeasibility-card">
            <div className="mono">{INFEASIBILITY_WORDING[r.status] ?? r.status}</div>
            {r.infeasibility && (
              <div className="muted">
                {r.infeasibility.reason_code} · closest {String(r.infeasibility.closest_action?.class ?? "")} · shortfall {r.infeasibility.shortfall_normalised}
              </div>
            )}
            <div className="caption">{DISCLAIMERS.DISC_INFEAS}</div>
          </div>
        )}
      </div>
    );
  }

  if (!r) return <div className="panel"><h3>Rescue table</h3><p className="muted">Run the rescue solver.</p></div>;
  return (
    <div className="panel">
      <h3>Rescue — exhaustive evaluation of the declared finite action set ({r.action_set_size} actions)</h3>
      <table>
        <thead>
          <tr><th>action</th><th>cost</th><th>φ</th><th>feasible</th><th>credible</th></tr>
        </thead>
        <tbody>
          {r.evaluated.map((e, i) => (
            <tr key={i}>
              <td className="mono">{e.action}</td>
              <td className="mono">{e.cost.toFixed(3)}</td>
              <td className="mono">{e.phi.toFixed(4)}</td>
              <td>{e.feasible ? "yes" : "no"}</td>
              <td>{e.credibility}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
