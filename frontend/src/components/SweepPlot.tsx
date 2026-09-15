import React from "react";
import Plot from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";
import { useStore } from "../state/store";

const Plotly = createPlotlyComponent(Plot);

export function SweepPlot() {
  const store = useStore();
  const sim = store.simulate;
  if (!sim) return <div className="panel"><h3>qNet & APD90 vs swept variable</h3><p className="muted">—</p></div>;

  const boundary = sim.qnet_boundary_C_per_F;
  return (
    <div className="panel">
      <h3>qNet & APD90 vs swept variable</h3>
      <div className="muted">
        model-defined boundary: qNet = 75% of drug-free control (declared convention, not a clinical threshold)
      </div>
      <Plotly
        data={[
          { y: [sim.qnet_C_per_F], name: "qNet (C/F)", type: "scatter", mode: "markers" },
          { y: [boundary], name: "boundary", type: "scatter", mode: "lines", line: { dash: "dash" } },
        ]}
        layout={{ height: 300, margin: { l: 60, r: 20, t: 20, b: 40 }, paper_bgcolor: "#101418", plot_bgcolor: "#101418", font: { color: "#d6dde3" } }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
}
