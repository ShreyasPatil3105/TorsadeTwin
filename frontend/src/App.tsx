import React, { useEffect, useState } from "react";
import { DisclaimerBar } from "./components/DisclaimerBar";
import { CredibilityBanner } from "./components/CredibilityBanner";
import { ScenarioPanel } from "./components/ScenarioPanel";
import { StatePanel } from "./components/StatePanel";
import { MarginPanel } from "./components/MarginPanel";
import { BindingPanel } from "./components/BindingPanel";
import { RescuePanel } from "./components/RescuePanel";
import { APTracePlot } from "./components/APTracePlot";
import { SweepPlot } from "./components/SweepPlot";
import { PhiCurvePlot } from "./components/PhiCurvePlot";
import { MechanismTable } from "./components/MechanismTable";
import { ScoreComparison } from "./components/ScoreComparison";
import { VerificationTable } from "./components/VerificationTable";
import { ProvenancePanel } from "./components/ProvenancePanel";
import { useStore } from "./state/store";
import { DISCLAIMERS, RESEARCH_FRAMING } from "./copy/strings";

export default function App() {
  const store = useStore();
  const [centerTab, setCenterTab] = useState<number>(0);
  const [bottomTab, setBottomTab] = useState<number>(0);

  useEffect(() => {
    store.health();
  }, []);

  const credibility = store.simulate?.credibility?.state ?? "UNVERIFIED";

  return (
    <div className="app">
      <header className="header">
        <div className="header-title">
          <span className="product">TorsadeTwin</span>
          <span className="subtitle">Mechanistic Cardiac Safety Margin + Rescue Engine</span>
        </div>
        <div className="header-chips">
          <span className="chip">model: {store.health?.model_id ?? "—"}</span>
          <span className="chip">config {store.health?.config_hash?.slice(0, 6) ?? "—"}</span>
          <span className="chip">OFFLINE</span>
          <span className={`chip cred-${credibility.toLowerCase()}`}>{credibility}</span>
        </div>
        <DisclaimerBar text={DISCLAIMERS.DISC_GLOBAL} />
      </header>

      <CredibilityBanner state={credibility} />

      <div className="research-framing">{RESEARCH_FRAMING}</div>

      <div className="layout">
        <aside className="left">
          <ScenarioPanel />
          <StatePanel />
        </aside>
        <main className="center">
          <div className="tabs">
            {["Action potential", "qNet & APD90 sweep", "Phi curves", "Rescue table"].map((t, i) => (
              <button key={t} className={i === centerTab ? "tab active" : "tab"} onClick={() => setCenterTab(i)}>
                {t}
              </button>
            ))}
          </div>
          {centerTab === 0 && <APTracePlot />}
          {centerTab === 1 && <SweepPlot />}
          {centerTab === 2 && <PhiCurvePlot />}
          {centerTab === 3 && <RescuePanel />}
        </main>
        <aside className="right">
          <MarginPanel />
          <BindingPanel />
          <RescuePanel compact />
          <div className="caption">{DISCLAIMERS.DISC_MARGIN}</div>
        </aside>
      </div>

      <footer className="bottom">
        <div className="tabs">
          {["Mechanism", "Clinical-score comparison", "Verification", "Provenance"].map((t, i) => (
            <button key={t} className={i === bottomTab ? "tab active" : "tab"} onClick={() => setBottomTab(i)}>
              {t}
            </button>
          ))}
        </div>
        {bottomTab === 0 && <MechanismTable />}
        {bottomTab === 1 && <ScoreComparison />}
        {bottomTab === 2 && <VerificationTable />}
        {bottomTab === 3 && <ProvenancePanel />}
      </footer>
    </div>
  );
}
