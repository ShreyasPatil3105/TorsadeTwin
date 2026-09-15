import React from "react";
import Plot from "plotly.js-dist-min";
import createPlotlyComponent from "react-plotly.js/factory";
import { useStore } from "../state/store";

const Plotly = createPlotlyComponent(Plot);

export function PhiCurvePlot() {
  const store = useStore();
  const m = store.margin;
  if (!m) return <div className="panel"><h3>Phi(K+) and Phi(exposure) curves with roots</h3><p className="muted">—</p></div>;

  return (
    <div className="panel">
      <h3>Phi curves with roots marked</h3>
      {m.axes.map((a) => (
        <div key={a.axis} className="muted mono">
          {a.axis}: roots at {a.all_roots.map((r) => r.toFixed(2)).join(", ") || "none"} · {a.monotonicity}
        </div>
      ))}
      <Plotly
        data={m.axes.map((a) => ({
          name: a.axis,
          type: "scatter",
          mode: "markers",
          x: a.all_roots,
          y: a.all_roots.map(() => 0),
        }))}
        layout={{ height: 260, margin: { l: 40, r: 20, t: 20, b: 40 }, paper_bgcolor: "#101418", plot_bgcolor: "#101418", font: { color: "#d6dde3" } }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
}
