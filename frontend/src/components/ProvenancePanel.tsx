import React from "react";
import { useStore } from "../state/store";

export function ProvenancePanel() {
  const store = useStore();
  return (
    <div className="panel">
      <h3>Provenance — SOURCE → PARAMETER → COMPUTATION → OUTPUT</h3>
      <div className="mono muted">
        config_hash: {store.health?.config_hash ?? "—"}
      </div>
      <div className="muted">
        Every number is traceable from DOI to parameter to computation to a reproducible result hash.
        Export JSON/PDF via /api/v1/report.
      </div>
    </div>
  );
}
