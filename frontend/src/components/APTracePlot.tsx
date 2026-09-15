import React from "react";
import Plot from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";
import { useStore } from "../state/store";

const Plotly = createPlotlyComponent(Plot);

export function APTracePlot() {
  const store = useStore();
  const sim = store.simulate;
  if (!sim?.trace) return <div className="panel"><h3>Action potential V(t) + I_net(t)</h3><p className="muted">Run a simulation to see the final beat.</p></div>;

  const { t_ms, v_mV, i_net_A_per_F } = sim.trace;
  return (
    <div className="panel">
      <h3>Action potential V(t) + I_net(t) — final beat (dt = {sim.trace.dt_ms} ms)</h3>
      <Plotly
        data={[
          { x: t_ms, y: v_mV, name: "V (mV)", mode: "lines", yaxis: "y" },
          { x: t_ms, y: i_net_A_per_F, name: "I_net (A/F)", mode: "lines", yaxis: "y2" },
        ]}
        layout={{
          height: 320,
          margin: { l: 50, r: 50, t: 20, b: 40 },
          yaxis: { title: "V (mV)" },
          yaxis2: { title: "I_net (A/F)", overlaying: "y", side: "right" },
          xaxis: { title: "t (ms)" },
          paper_bgcolor: "#101418",
          plot_bgcolor: "#101418",
          font: { color: "#d6dde3" },
        }}
        config={{ displayModeBar: false }}
      />
      {sim.ra.flags.length > 0 && <div className="muted">RA annotation: {sim.ra.flags.join(", ")} ({sim.ra.status})</div>}
    </div>
  );
}
