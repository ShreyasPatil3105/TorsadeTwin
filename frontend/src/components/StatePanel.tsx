import React from "react";
import { useStore } from "../state/store";
import { CL_EXCLUDED_TOOLTIP, MG2_NOT_MODELLED } from "../copy/strings";

export function StatePanel() {
  const store = useStore();
  const req = store.request;

  return (
    <div className="panel">
      <h3>State</h3>
      <div className="field">
        <label>Extracellular K+ (mM)</label>
        <input
          type="range"
          min={2.5}
          max={7.0}
          step={0.1}
          value={req.k_o_mM}
          onChange={(e) => store.setRequest({ k_o_mM: Number(e.target.value) })}
        />
        <span className="mono">{req.k_o_mM.toFixed(1)}</span>
      </div>
      <div className="field">
        <label title={CL_EXCLUDED_TOOLTIP}>Cycle length (ms) — greyed for margin (CL_EXCLUDED_PROTOCOL_BOUND)</label>
        <input
          type="range"
          min={500}
          max={2000}
          step={100}
          value={req.cl_ms}
          disabled
          onChange={(e) => store.setRequest({ cl_ms: Number(e.target.value) })}
        />
        <span className="mono">{req.cl_ms}</span>
      </div>
      <div className="field disabled-row" title={MG2_NOT_MODELLED}>
        <label>Mg2+</label>
        <span className="mono">NOT MODELLED</span>
      </div>
      <div className="buttons">
        <button onClick={store.runSimulate}>Simulate</button>
        <button onClick={store.runMargin}>Margin</button>
        <button onClick={store.runRescue}>Run rescue</button>
        <button onClick={store.runVerify}>Verify</button>
      </div>
      {store.loading && <div className="progress mono">computing… {store.loading}</div>}
    </div>
  );
}
