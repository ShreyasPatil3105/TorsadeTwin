import React, { useEffect, useState } from "react";
import { api, Scenario } from "../api/client";
import { useStore } from "../state/store";

export function ScenarioPanel() {
  const store = useStore();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);

  useEffect(() => {
    api.scenarios().then((r) => setScenarios((r.scenarios as unknown as Scenario[]) ?? [])).catch(() => {});
  }, []);

  const load = (id: string) => {
    const sc = scenarios.find((s) => s.scenario_id === id);
    if (!sc) return;
    store.setRequest({
      drugs: sc.state.drugs.map((d) => ({ drug_id: d.drug_id, exposure_multiplier: d.exposure_multiplier })),
      k_o_mM: sc.state.k_o_mM,
      cl_ms: sc.state.cl_ms,
    });
  };

  return (
    <div className="panel">
      <h3>Scenario</h3>
      <select data-testid="scenario-select" onChange={(e) => load(e.target.value)}>
        {scenarios.map((s) => (
          <option key={s.scenario_id} value={s.scenario_id}>
            {s.scenario_id}
          </option>
        ))}
      </select>
      <div className="synthetic-badge">synthetic · declared non-identifiable state</div>
    </div>
  );
}
