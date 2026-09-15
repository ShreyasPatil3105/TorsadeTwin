const API_BASE = (window.TORSADETWIN_API_BASE || "").replace(/\/$/, "");
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];

const state = {
  drugs: [], scenarios: [], health: null, validation: null,
  selectedDrug: "dofetilide", exposure: 1, k: 5.4, cl: 2000,
  solver: "standard", comboRule: "indep_mult",
  simulate: null, margin: null, rescue: null, blindspot: null,
  busy: false, error: null, activeTab: "mechanism", apiOnline: false,
};

const frozenCopy = {
  global: "Research prototype. In-silico model output only. Not clinically validated. Not for clinical decision-making.",
  margin: "Margin = weighted distance in modelled-state space to the model-defined qNet boundary. It is NOT a probability of clinical harm.",
  rescue: "Rescue = minimum-cost element of a declared finite action set that restores the target margin **in this model**. It is not a treatment recommendation.",
  infeas: "Exhaustive over the declared finite action set only. Says nothing about actions outside that set.",
  score: "Comparison shows the score's insensitivity to a modelled variable over an interval. It does not establish that the score is incorrect.",
  unverified: "NOT TRUSTWORTHY — numerical credibility checks did not pass. Result shown for debugging only."
};

function esc(v){return String(v ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function fmt(v,n=5){return Number.isFinite(Number(v)) ? Number(v).toFixed(n) : "—";}
function pct(v){return Number.isFinite(Number(v)) ? `${Number(v)>=0?"+":""}${Number(v).toFixed(1)}%` : "—";}
function api(path, opts={}) {
  return fetch(`${API_BASE}/api/v1${path}`, {headers:{"Content-Type":"application/json",...(opts.headers||{})}, ...opts})
    .then(async r => { const data=await r.json().catch(()=>({})); if(!r.ok){const e=new Error(data.detail||data.message||`HTTP ${r.status}`);e.payload=data;throw e;}return data;});
}
function setBusy(v){state.busy=v; render();}
function credClass(c){const s=(c?.state||c||"UNVERIFIED").toUpperCase();return s==="VERIFIED"?"verified":s==="FAILED"?"failed":"unverified";}
function credLabel(c){return (c?.state||c||"UNVERIFIED").toUpperCase();}
function toast(msg, kind="info"){const el=document.createElement("div");el.className=`toast ${kind}`;el.textContent=msg;document.body.appendChild(el);setTimeout(()=>el.remove(),4200);}
function download(name, text, type="application/json"){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500);}

async function boot(){
  render();
  try {
    const [health, drugs, scenarios, validation] = await Promise.all([
      api("/health"), api("/drugs"), api("/scenarios"), api("/validation")
    ]);
    state.health=health; state.drugs=drugs.drugs||[]; state.scenarios=scenarios.scenarios||[]; state.validation=validation; state.apiOnline=true;
    if(!state.drugs.some(d=>d.drug_id===state.selectedDrug)) state.selectedDrug=state.drugs[0]?.drug_id||"";
    render();
  } catch(e) {
    state.apiOnline=false; state.error=e.message;
    render();
  }
}
function drug(){return state.drugs.find(d=>d.drug_id===state.selectedDrug)||{};}
function scenarioPayload(returnTrace=false){
  return {drugs:state.selectedDrug?[{drug_id:state.selectedDrug,exposure_multiplier:Number(state.exposure)}]:[],
    k_o_mM:Number(state.k),cl_ms:Number(state.cl),cell_type:"endo",solver_profile:state.solver,
    return_trace:returnTrace,combo_rule:state.comboRule};
}

async function runSim(){
  if(!state.apiOnline) return toast("Backend is not reachable. Start FastAPI first.","error");
  state.error=null; setBusy(true);
  try { state.simulate=await api("/simulate",{method:"POST",body:JSON.stringify(scenarioPayload(true))}); state.activeTab="mechanism"; toast("Simulation completed","success"); }
  catch(e){state.error=e.message;toast(e.message,"error");}
  finally{setBusy(false);}
}
async function runMargin(){
  if(!state.apiOnline)return toast("Backend is not reachable.","error");
  state.error=null; setBusy(true);
  try {
    const axes=["k_o_mM",...(state.selectedDrug?[`exposure:${state.selectedDrug}`]:[])];
    state.margin=await api("/margin",{method:"POST",body:JSON.stringify({...scenarioPayload(false),axes,max_evals:300})});
    state.activeTab="margin"; toast("Margin search completed","success");
  } catch(e){state.error=e.message;toast(e.message,"error");}
  finally{setBusy(false);}
}
async function runRescue(){
  if(!state.apiOnline)return toast("Backend is not reachable.","error");
  state.error=null; setBusy(true);
  try {
    state.rescue=await api("/rescue",{method:"POST",body:JSON.stringify({...scenarioPayload(false),tau:.05,cost_weights:{w_K:1,w_E:1,w_D:6},allow_discontinuation:true,compute_post_margin:true})});
    state.activeTab="rescue"; toast("Rescue search completed","success");
  } catch(e){state.error=e.message;toast(e.message,"error");}
  finally{setBusy(false);}
}
async function runVerify(){
  if(!state.apiOnline)return toast("Backend is not reachable.","error");
  setBusy(true); try{state.validation=await api("/verify",{method:"POST",body:"{}"});state.activeTab="verification";}catch(e){toast(e.message,"error")}finally{setBusy(false)}
}
async function runBlindspot(){
  if(!state.apiOnline)return;
  setBusy(true);
  try{
    const base={drugs:state.selectedDrug?[{drug_id:state.selectedDrug,exposure_multiplier:Number(state.exposure)}]:[],k_o_mM:Number(state.k),cl_ms:2000,cell_type:"endo",solver_profile:"standard",combo_rule:"indep_mult"};
    state.blindspot=await api("/blindspot",{method:"POST",body:JSON.stringify({
      base_state:base,
      sweep:{variable:"k_o_mM",hi:4.5,lo:3.6,step:.1},
      score_inputs:{score_id:"tisdale_2013",age_ge_68:true,loop_diuretic:true,heart_failure:true,acute_mi:false,sepsis:false,female_sex:null,admission_qtc_ge_450:null}
    })});
    state.activeTab="score";
  }catch(e){toast(e.message,"error")}finally{setBusy(false)}
}
async function exportReport(){
  if(!state.apiOnline)return;
  setBusy(true);
  try{
    const data=await api("/report",{method:"POST",body:JSON.stringify({
      include:["simulation","margin","rescue","provenance"],state:scenarioPayload(false),format:["json"],result_hashes:[]
    })});
    download(`torsadetwin-${Date.now()}.json`,JSON.stringify(data,null,2));
    toast("JSON report exported","success");
  }catch(e){toast(e.message,"error")}finally{setBusy(false)}
}

function render(){
  const root=$("#app");
  root.innerHTML=`
  <div class="shell">
    <aside class="rail">
      <div class="brand-mini"><span class="pulse-mark"></span><span>TorsadeTwin</span></div>
      <nav>
        ${nav("overview","Overview","Complete workflow","⌂")}
        ${nav("new","New Analysis","Run a scenario","＋")}
        ${nav("drugs","Drug Library","6 curated drugs","◈")}
        ${nav("history","Results History","Current session","↺")}
        ${nav("validation","Validation","Model verification","✓")}
        ${nav("docs","Documentation","Methods & data","▤")}
      </nav>
      <div class="rail-bottom">
        <div class="model-card">
          <div class="eyebrow">MODEL</div>
          <strong>${esc(state.health?.model_id||"ORd-CiPA-v1.0")}</strong>
          <span>${state.health?.model_hash ? state.health.model_hash.slice(0,12)+"…" : "awaiting backend"}</span>
        </div>
        <div class="rail-foot">VIT Chennai<br><span>Computational Cardiac Electrophysiology</span></div>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <div class="wordmark">Torsade<span>Twin</span></div>
          <div class="subtitle">COMPUTATIONAL CARDIAC SAFETY RESEARCH</div>
        </div>
        <div class="top-meta">
          <div class="claim">Mechanistic models. Quantifiable margins. Safer possibilities.</div>
          <div class="status-row">
            <span class="status-dot ${state.apiOnline?"ok":"warn"}"></span>
            ${state.apiOnline?"API CONNECTED":"BACKEND OFFLINE"}
            <span class="divider"></span>
            ${credLabel(state.validation?.aggregate||state.simulate?.credibility)}
            <span class="version">${esc(state.health?.version||"0.1.0")}</span>
          </div>
        </div>
      </header>

      <div class="research-banner"><span class="shield">◆</span><span>${frozenCopy.global}</span></div>

      <section class="workflow">
        ${step(1,"Scenario","Define drug & conditions",true)}
        ${arrow()}${step(2,"Simulation","Electrophysiology model",!!state.simulate)}
        ${arrow()}${step(3,"Margin","Distance to boundary",!!state.margin)}
        ${arrow()}${step(4,"Rescue","Explore interventions",!!state.rescue)}
        ${arrow()}${step(5,"Compare","Before / after",!!state.rescue)}
        ${arrow()}${step(6,"Report","Export results",false)}
      </section>

      ${state.error?`<div class="error-strip"><b>Request error</b><span>${esc(state.error)}</span></div>`:""}

      <section class="workspace">
        <div class="panel scenario-panel">
          <div class="section-kicker">01 / SCENARIO</div>
          <div class="section-title">Define your scenario</div>
          <p class="section-desc">Declare the modelled state to evaluate. Inputs remain within the backend's permitted domain.</p>
          <div class="preset-row">
            ${(state.drugs.length?state.drugs:[]).map(d=>`<button class="preset ${d.drug_id===state.selectedDrug?"active":""}" data-drug="${esc(d.drug_id)}">${esc(d.drug_name)}</button>`).join("")}
          </div>
          <div class="form-grid">
            <label>DRUG<select id="drug">${state.drugs.map(d=>`<option value="${esc(d.drug_id)}" ${d.drug_id===state.selectedDrug?"selected":""}>${esc(d.drug_name)} · ${d.cmax_free_nM} nM free Cmax</option>`).join("")}</select></label>
            <label>EXPOSURE MULTIPLIER <div class="range-wrap"><input id="exposure" type="range" min="0" max="4" step=".25" value="${state.exposure}"><output>${fmt(state.exposure,2)}×</output></div><span class="hint">0–25× accepted by API; slider shown to 4× for controlled exploration.</span></label>
            <label>EXTRACELLULAR K⁺ <div class="range-wrap"><input id="k" type="range" min="2.5" max="7" step=".1" value="${state.k}"><output>${fmt(state.k,1)} mM</output></div><span class="hint">Permitted domain: 2.5–7.0 mM</span></label>
            <label>CYCLE LENGTH <div class="range-wrap"><input id="cl" type="range" min="500" max="2000" step="100" value="${state.cl}" ${state.margin?"":"disabled"}><output>${state.cl} ms</output></div><span class="hint">qNet / Margin / Rescue require CL 2000 ms.</span></label>
          </div>
          <div class="action-row">
            <button class="primary" id="simulate" ${state.busy?"disabled":""}><span>Run simulation</span><b>↗</b></button>
            <button class="secondary" id="margin" ${state.busy?"disabled":""}>Calculate margin</button>
            <button class="secondary" id="rescue" ${state.busy||!state.simulate?"disabled":""}>Run rescue</button>
          </div>
          <div class="micro-note">Cell type <b>endo</b> · Solver <b>${esc(state.solver)}</b> · Combo rule <b>indep_mult</b> · deterministic float64</div>
        </div>

        <div class="panel quick-panel">
          <div class="section-kicker">LIVE STATE</div>
          <div class="quick-head"><span>System status</span><span class="tiny-pill ${state.apiOnline?"good":"amber"}">${state.apiOnline?"ONLINE":"OFFLINE"}</span></div>
          <div class="readout"><span>Model</span><b>${esc(state.health?.model_id||"—")}</b></div>
          <div class="readout"><span>Data integrity</span><b>${esc(state.health?.data_integrity||"—")}</b></div>
          <div class="readout"><span>Verification</span><b>${esc(state.validation?.aggregate||"—")}</b></div>
          <div class="readout"><span>Battery</span><b>${state.health?.battery_present?"present":"not present"}</b></div>
          <div class="quick-actions"><button id="verify" class="text-btn">Open verification →</button><button id="report" class="text-btn">Export JSON →</button></div>
        </div>
      </section>

      ${resultsSection()}
      ${tabsSection()}

      <footer class="footer">
        <div><b>TorsadeTwin</b> · VIT Chennai · In-silico research prototype</div>
        <div>For research use only · Not for clinical decision-making</div>
      </footer>
    </main>
  </div>`;
  bind();
}

function nav(id,title,sub,icon){return `<button class="nav-item ${id==="overview"?"selected":""}" data-nav="${id}"><span class="nav-icon">${icon}</span><span><b>${title}</b><small>${sub}</small></span></button>`}
function arrow(){return `<span class="flow-arrow">→</span>`}
function step(n,t,s,on){return `<div class="flow-step ${on?"on":""}"><span class="step-num">${n}</span><div><b>${t}</b><small>${s}</small></div></div>`}

function resultsSection(){
  const s=state.simulate, m=state.margin, r=state.rescue;
  if(!s && !m && !r) return `<section class="empty-state panel"><div class="empty-symbol">∿</div><div><div class="section-kicker">ANALYSIS WORKBENCH</div><h2>Awaiting a declared scenario</h2><p>Run a simulation to populate electrophysiology, then calculate Margin and explore the finite Rescue action set.</p></div></section>`;
  const q=s?.qnet_C_per_F, ctrl=s?.qnet_ctrl_C_per_F, bd=s?.qnet_boundary_C_per_F;
  const phi=s?.phi_C_per_F ?? (m?.phi_now);
  const delta=Number.isFinite(q)&&Number.isFinite(ctrl)?(q/ctrl-1)*100:null;
  const status=m?.m_status||"PENDING";
  return `<section class="results">
    <div class="result-head"><div><div class="section-kicker">02 / RESULTS</div><h2>Analysis output</h2></div>
      <div class="result-actions"><span class="tiny-pill ${credClass(s?.credibility||m?.credibility)}">${credLabel(s?.credibility||m?.credibility)}</span><span class="mono">Φ evaluations ${m?.n_phi_evals??"—"}</span><button id="report2" class="secondary">Export report</button></div>
    </div>
    <div class="metric-grid">
      ${metric("CONTROL qNet",fmt(ctrl,5),"µC/µF","reference")}
      ${metric("SCENARIO qNet",fmt(q,5),"µC/µF",delta!==null?pct(delta):"")}
      ${metric("MODEL-DEFINED BOUNDARY",fmt(bd,5),"µC/µF","75% of control")}
      ${metric("Φ = qNet − boundary",fmt(phi,7),"µC/µF",status)}
    </div>
    <div class="viz-grid">
      <div class="panel chart-panel"><div class="panel-head"><h3>Action potential</h3><span>final analysis beat</span></div>${traceSVG(s?.trace)}</div>
      <div class="panel metrics-panel"><div class="panel-head"><h3>Electrophysiological metrics</h3><span>scenario vs control</span></div>
        <table><thead><tr><th>Metric</th><th>Value</th><th>Unit</th></tr></thead><tbody>
          ${row("qNet",fmt(q,6),"µC/µF")} ${row("APD90",fmt(s?.apd90_ms,2),"ms")} ${row("Vrest",fmt(s?.v_rest_mV,2),"mV")} ${row("Vpeak",fmt(s?.v_peak_mV,2),"mV")} ${row("dV/dt max",fmt(s?.dvdt_max_mV_per_ms,2),"mV/ms")}
        </tbody></table>
      </div>
      <div class="panel margin-visual"><div class="panel-head"><h3>Margin visualization</h3><span>model-defined</span></div>${marginBar(q,bd,m)}</div>
    </div>
    ${r?rescueSummary(r):""}
  </section>`;
}
function metric(label,value,unit,note){return `<div class="metric"><span>${label}</span><strong>${value}</strong><small>${unit} ${note?`· ${esc(note)}`:""}</small></div>`}
function row(a,b,c){return `<tr><td>${a}</td><td class="mono">${b}</td><td>${c}</td></tr>`}
function traceSVG(trace){
  if(!trace?.t_ms?.length)return `<div class="chart-empty"><span>No trace returned.</span><small>Run simulation with trace enabled to inspect the final beat.</small></div>`;
  const t=trace.t_ms, v=trace.v_mV; const w=760,h=290,p=42;
  const minT=Math.min(...t),maxT=Math.max(...t),minV=Math.min(...v),maxV=Math.max(...v);
  const x=i=>p+(t[i]-minT)/(maxT-minT||1)*(w-2*p), y=i=>h-p-(v[i]-minV)/(maxV-minV||1)*(h-2*p);
  let d=""; const step=Math.max(1,Math.floor(t.length/500)); for(let i=0;i<t.length;i+=step)d+=(i===0?"M":"L")+x(i).toFixed(1)+","+y(i).toFixed(1);
  return `<svg viewBox="0 0 ${w} ${h}" class="trace" role="img" aria-label="Action potential voltage trace">
    <g class="grid"><line x1="${p}" y1="${p}" x2="${p}" y2="${h-p}"/><line x1="${p}" y1="${h-p}" x2="${w-p}" y2="${h-p}"/>
    <line x1="${p}" y1="${h/2}" x2="${w-p}" y2="${h/2}"/></g>
    <path d="${d}" class="trace-line"/><text x="${p}" y="${p-12}">${esc(maxV.toFixed(0))} mV</text><text x="${p}" y="${h-p+24}">${esc(minV.toFixed(0))} mV</text>
    <text x="${p}" y="${h-8}">${esc(minT.toFixed(0))} ms</text><text x="${w-p-35}" y="${h-8}">${esc(maxT.toFixed(0))} ms</text>
    <text x="${w/2-40}" y="${h-8}" class="axis-title">time (ms)</text><text x="10" y="${h/2}" class="axis-title" transform="rotate(-90 10 ${h/2})">voltage (mV)</text>
  </svg>`;
}
function marginBar(q,bd,m){
  const lo=Number.isFinite(Number(q))?Math.min(q,bd||q)*.85:0, hi=Number.isFinite(Number(bd))?Math.max(q,bd)*1.15:1;
  const pos=v=>Math.max(3,Math.min(97,(v-lo)/(hi-lo||1)*100)); const qp=pos(q),bp=pos(bd);
  return `<div class="margin-scale"><div class="scale-labels"><span>Lower qNet</span><span>Higher qNet</span></div><div class="scale"><div class="unsafe"></div><div class="safe"></div><i class="tick boundary" style="left:${bp}%"></i><i class="tick scenario" style="left:${qp}%"></i></div>
    <div class="markers"><span style="left:${qp}%"><b>Scenario</b><strong>${fmt(q,5)}</strong></span><span style="left:${bp}%"><b>Boundary</b><strong>${fmt(bd,5)}</strong></span></div>
    <div class="margin-copy"><strong>${m?.m_label||statusLabel(m?.m_status)}</strong><p>${frozenCopy.margin}</p></div></div>`;
}
function statusLabel(s){return s==="SAMPLED_UB"?"≤ upper bound":s==="BUDGET_EXCEEDED"?"Budget exceeded":s||"Awaiting margin";}
function rescueSummary(r){
  const best=r.best_action;
  return `<div class="rescue-grid"><div class="panel rescue-table"><div class="panel-head"><h3>Rescue analysis</h3><span>${esc(r.status||"")}</span></div>
    <table><thead><tr><th>Action</th><th>Cost</th><th>Φ after</th><th>Status</th></tr></thead><tbody>${(r.evaluated||[]).map(e=>`<tr><td>${esc(e.action)}</td><td class="mono">${fmt(e.cost,3)}</td><td class="mono">${fmt(e.phi,6)}</td><td><span class="state-dot ${e.feasible?"good":"neutral"}">${e.feasible?"FEASIBLE":"NOT FEASIBLE"}</span></td></tr>`).join("")}</tbody></table></div>
    <div class="panel best-card"><div class="section-kicker">BEST MODELED RESCUE</div>${best?`<h3>${esc(best.class)}${best.param?.k_o_mM!=null?` · K⁺ ${fmt(best.param.k_o_mM,1)} mM`:""}</h3><div class="best-number">${fmt(best.phi_after,6)}</div><span>Φ after · margin ${fmt(best.margin_after,4)}</span>`:`<h3>No feasible single action</h3><p>${esc(r.infeasibility?.explanation||"See the evaluated action set.")}</p>`}<div class="notice">${frozenCopy.rescue}</div></div></div>`;
}
function tabsSection(){
  return `<section class="lower">
    <div class="tabs">${["mechanism","margin","rescue","score","verification","provenance"].map(t=>`<button class="${state.activeTab===t?"active":""}" data-tab="${t}">${t==="mechanism"?"Mechanism":t==="margin"?"Margin detail":t==="rescue"?"Rescue":t==="score"?"Score comparison":t==="verification"?"Verification":"Provenance"}</button>`).join("")}</div>
    <div class="tab-content">${tabContent()}</div>
  </section>`;
}
function tabContent(){
  if(state.activeTab==="mechanism")return mechanismTab();
  if(state.activeTab==="margin")return marginTab();
  if(state.activeTab==="rescue")return rescueTab();
  if(state.activeTab==="score")return scoreTab();
  if(state.activeTab==="verification")return verificationTab();
  return provenanceTab();
}
function mechanismTab(){
  const d=drug(); return `<div class="two-col"><div><div class="section-kicker">CHANNEL PANEL</div><h3>Pharmacology registry</h3><p class="muted">Runtime block values are derived from the verified registry; unavailable/rejected channels are never invented.</p>
  <table><thead><tr><th>Channel</th><th>IC50 (nM)</th><th>Hill</th><th>Verification</th><th>Source</th></tr></thead><tbody>${(d.channels||[]).map(c=>`<tr><td>${esc(c.channel)}</td><td class="mono">${c.ic50_nM??"NA"}</td><td class="mono">${c.hill??"—"}</td><td>${esc(c.verification_status)}</td><td class="mono source">${esc(c.source_doi||"—")}</td></tr>`).join("")}</tbody></table></div>
  <div class="assumption-box"><div class="section-kicker">MODEL SCOPE</div><h3>Explicit exclusions</h3><div class="exclusion"><b>Mg²⁺</b><span>NOT MODELLED</span></div><p>The selected v1.0 model contains no Mg²⁺-dependent conductance or Mg²⁺ block term.</p><div class="exclusion"><b>Cell type</b><span>ENDO ONLY</span></div><p>Single ventricular cell; no electrotonic coupling or re-entry claim.</p></div></div>`;
}
function marginTab(){
  const m=state.margin;if(!m)return `<div class="empty-tab"><h3>Margin not calculated</h3><p>Run Calculate margin to populate the adaptive boundary search.</p></div>`;
  return `<div class="two-col"><div><div class="section-kicker">BOUNDARY SEARCH</div><h3>${esc(m.m_label||"Model-defined margin")}</h3><div class="large-number">${m.m_status==="SAMPLED_UB"?"≤ ":""}${fmt(m.m_signed,4)} <small>normalised units</small></div><p>${frozenCopy.margin}</p>
  <table><thead><tr><th>Axis</th><th>Distance</th><th>Critical value</th><th>Direction</th><th>Reachable</th></tr></thead><tbody>${(m.axes||[]).map(a=>`<tr><td>${esc(a.axis)}</td><td class="mono">${a.distance==null?"—":fmt(a.distance,4)}</td><td class="mono">${a.critical_raw_value==null?"—":fmt(a.critical_raw_value,3)}</td><td>${esc(a.direction||"—")}</td><td>${a.reachable?"YES":"NO"}</td></tr>`).join("")}</tbody></table></div>
  <div class="binding"><div class="section-kicker">BINDING CONSTRAINT</div><h3>${esc(m.binding_constraint?.axis||"—")}</h3><p>Critical value: <b>${fmt(m.binding_constraint?.critical_raw_value,4)}</b></p><p>Alternative axis: ${esc(m.binding_constraint?.alternative_axis||"—")}</p><p class="muted">Evaluations: ${m.n_phi_evals??"—"} · ${esc(m.m_status)}</p></div></div>`;
}
function rescueTab(){
  if(!state.rescue)return `<div class="empty-tab"><h3>Rescue not run</h3><p>Run rescue after a scenario simulation.</p></div>`;
  const r=state.rescue;return `<div><div class="rescue-title"><div><div class="section-kicker">FINITE ACTION SEARCH</div><h3>${esc(r.status)}</h3></div><span class="tiny-pill">${r.action_set_size} actions · ${r.n_noncredible} noncredible</span></div>
  <table><thead><tr><th>Action</th><th>Cost</th><th>Φ</th><th>Credibility</th><th>Feasible</th></tr></thead><tbody>${(r.evaluated||[]).map(e=>`<tr><td>${esc(e.action)}</td><td class="mono">${fmt(e.cost,3)}</td><td class="mono">${fmt(e.phi,6)}</td><td>${esc(e.credibility)}</td><td>${e.feasible?"YES":"NO"}${e.skipped_out_of_box?" · SKIPPED_OUT_OF_BOX":""}</td></tr>`).join("")}</tbody></table><div class="notice">${frozenCopy.rescue}</div>${r.infeasibility?`<div class="infeas"><b>${esc(r.infeasibility.reason_code)}</b><p>${esc(r.infeasibility.explanation)}</p><p>Closest action: ${esc(JSON.stringify(r.infeasibility.closest_action))}</p><p>${frozenCopy.infeas}</p></div>`:""}</div>`;
}
function scoreTab(){
  if(!state.blindspot)return `<div class="empty-tab"><h3>Score comparison</h3><p>Run the blind-spot comparison to inspect the score against the mechanistic sweep.</p><button class="secondary" id="blindspot">Run comparison</button></div>`;
  return `<div><div class="section-kicker">CLINICAL-SCORE COMPARISON</div><h3>Mechanistic margin vs Tisdale score</h3><p class="muted">${esc(state.blindspot.verdict||state.blindspot.audit_status||"Comparison returned.")}</p><div class="notice">${frozenCopy.score}</div></div>`;
}
function verificationTab(){
  const v=state.validation;if(!v)return `<div class="empty-tab"><h3>Verification unavailable</h3></div>`;
  const checks=v.checks||[];return `<div><div class="verify-head"><div><div class="section-kicker">VERIFICATION BATTERY</div><h3>${esc(v.aggregate||"UNVERIFIED")}</h3><p class="muted">Configuration hash ${esc(v.battery?.config_hash||v.config_hash||"—")}</p></div><button class="secondary" id="verify2">Refresh verification</button></div>
  <table><thead><tr><th>ID</th><th>Check</th><th>Tier</th><th>State</th><th>Detail</th></tr></thead><tbody>${checks.map(c=>`<tr><td class="mono">${esc(c.id)}</td><td>${esc(c.name)}</td><td>${esc(c.tier)}</td><td><span class="state-dot ${c.state==="PASS"?"good":c.state==="FAIL"?"bad":"neutral"}">${esc(c.state)}</span></td><td class="muted">${esc(c.detail||"")}</td></tr>`).join("")}</tbody></table></div>`;
}
function provenanceTab(){
  const h=state.health||{};return `<div class="provenance-grid"><div><div class="section-kicker">TRACEABILITY</div><h3>Source → parameter → computation → output</h3><div class="chain">${["Published pharmacology","Verified registry","ORd-CiPA model artefact","CVODES simulation","qNet / APD90","Margin / Rescue","Reproducible result hash"].map((x,i)=>`<div><span>${String(i+1).padStart(2,"0")}</span><b>${x}</b></div>`).join("")}</div></div><div class="hashes"><div><span>Model hash</span><code>${esc(h.model_hash||"—")}</code></div><div><span>Config hash</span><code>${esc(h.config_hash||"—")}</code></div><div><span>Offline</span><code>${h.offline?"TRUE":"—"}</code></div></div></div>`;
}
function bind(){
  $("#drug")?.addEventListener("change",e=>{state.selectedDrug=e.target.value;state.simulate=null;state.margin=null;state.rescue=null;render()});
  $("#exposure")?.addEventListener("input",e=>{state.exposure=Number(e.target.value);e.target.nextElementSibling.value=`${fmt(state.exposure,2)}×`});
  $("#k")?.addEventListener("input",e=>{state.k=Number(e.target.value);e.target.nextElementSibling.value=`${fmt(state.k,1)} mM`});
  $("#cl")?.addEventListener("input",e=>{state.cl=Number(e.target.value);e.target.nextElementSibling.value=`${state.cl} ms`});
  $$(".preset").forEach(b=>b.addEventListener("click",()=>{state.selectedDrug=b.dataset.drug;render()}));
  $("#simulate")?.addEventListener("click",runSim);$("#margin")?.addEventListener("click",runMargin);$("#rescue")?.addEventListener("click",runRescue);
  $("#verify")?.addEventListener("click",()=>{state.activeTab="verification";render()});$("#verify2")?.addEventListener("click",runVerify);
  $("#report")?.addEventListener("click",exportReport);$("#report2")?.addEventListener("click",exportReport);
  $("#blindspot")?.addEventListener("click",runBlindspot);
  $$("[data-tab]").forEach(b=>b.addEventListener("click",()=>{state.activeTab=b.dataset.tab;render()}));
  $$("[data-nav]").forEach(b=>b.addEventListener("click",()=>{if(b.dataset.nav==="validation"){state.activeTab="verification";render()}else if(b.dataset.nav==="drugs"){state.activeTab="mechanism";render()}else window.scrollTo({top:0,behavior:"smooth"})}));
}
boot();
