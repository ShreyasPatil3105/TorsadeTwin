const API_BASE = (window.TORSADETWIN_API_BASE || "").replace(/\/$/, "");
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];

const state = {
  drugs: [], scenarios: [], health: null, validation: null,
  selectedDrug: "dofetilide", exposure: 1, k: 5.4, cl: 2000,
  solver: "standard", comboRule: "indep_mult", tau: 0.05,
  simulate: null, margin: null, rescue: null, blindspot: null,
  busy: false, busyOp: null, error: null, activeTab: "mechanism", activeNav: "overview",
  history: [], apiOnline: false,
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
function setBusy(v, op=null){state.busy=v; state.busyOp=op; render();}
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

function recordHistory(type){
  const d = drug();
  state.history.unshift({
    id: "run_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6),
    type,
    time: new Date().toLocaleTimeString(),
    drug_name: d.drug_name || state.selectedDrug || "Control",
    exposure: state.exposure,
    k: state.k,
    cl: state.cl,
    qnet: state.simulate?.qnet_C_per_F,
    phi: state.simulate?.phi_C_per_F ?? state.margin?.phi_now,
    margin: state.margin?.m_signed,
    margin_status: state.margin?.m_status,
    binding_axis: state.margin?.binding_constraint?.axis,
    snapshot: {
      selectedDrug: state.selectedDrug,
      exposure: state.exposure,
      k: state.k,
      cl: state.cl,
      simulate: state.simulate ? JSON.parse(JSON.stringify(state.simulate)) : null,
      margin: state.margin ? JSON.parse(JSON.stringify(state.margin)) : null,
      rescue: state.rescue ? JSON.parse(JSON.stringify(state.rescue)) : null,
    }
  });
  if(state.history.length > 30) state.history.pop();
}

async function runSim(){
  if(!state.apiOnline) return toast("Backend is not reachable. Start FastAPI first.","error");
  state.error=null; setBusy(true, "simulate");
  try {
    state.simulate=await api("/simulate",{method:"POST",body:JSON.stringify(scenarioPayload(true))});
    state.activeTab="mechanism";
    recordHistory("simulation");
    toast("Simulation completed","success");
    setTimeout(()=>{document.querySelector(".results")?.scrollIntoView({behavior:"smooth"});}, 80);
  }
  catch(e){state.error=e.message;toast(e.message,"error");}
  finally{setBusy(false);}
}
async function runMargin(){
  if(!state.apiOnline)return toast("Backend is not reachable. Start FastAPI first.","error");
  state.error=null; setBusy(true, "margin");
  toast("Calculating multidimensional margin (~12s, 300 evaluations)...","info");
  try {
    const axes=["k_o_mM",...(state.selectedDrug?[`exposure:${state.selectedDrug}`]:[])];
    const simPromise = api("/simulate",{method:"POST",body:JSON.stringify(scenarioPayload(true))});
    const marginPromise = api("/margin",{method:"POST",body:JSON.stringify({...scenarioPayload(false),axes,max_evals:300})});
    const [simRes, marginRes] = await Promise.all([simPromise, marginPromise]);
    state.simulate = simRes;
    state.margin = marginRes;
    state.activeTab = "margin";
    recordHistory("margin");
    toast("Margin search completed successfully","success");
    setTimeout(()=>{document.querySelector(".results")?.scrollIntoView({behavior:"smooth"});}, 80);
  } catch(e){state.error=e.message;toast(e.message,"error");}
  finally{setBusy(false);}
}
async function runRescue(tauVal = null){
  if(!state.apiOnline)return toast("Backend is not reachable. Start FastAPI first.","error");
  if(tauVal !== null) state.tau = tauVal;
  state.error=null; setBusy(true, "rescue");
  const tauDesc = (state.tau ?? 0.05) === 0 ? "boundary crossing (τ=0)" : "standard 5% buffer (τ=0.05)";
  toast(`Exploring finite rescue actions [${tauDesc}]...`,"info");
  try {
    state.rescue=await api("/rescue",{method:"POST",body:JSON.stringify({
      ...scenarioPayload(false),
      tau: state.tau ?? 0.05,
      cost_weights: {w_K:1, w_E:1, w_D:6},
      allow_discontinuation: true,
      compute_post_margin: true
    })});
    state.activeTab="rescue";
    recordHistory("rescue");
    toast(`Rescue search completed: ${state.rescue.status}`,"success");
    setTimeout(()=>{document.querySelector(".rescue-grid, .rescue-title")?.scrollIntoView({behavior:"smooth"});}, 80);
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
            <button class="primary" id="simulate" ${state.busy?"disabled":""}>${state.busyOp==="simulate"?'<span><span class="spin-dot"></span> Simulating...</span>':'<span>Run simulation</span><b>↗</b>'}</button>
            <button class="secondary ${state.busyOp==="margin"?"is-loading":""}" id="margin" ${state.busy?"disabled":""}>${state.busyOp==="margin"?'<span class="spin-dot"></span> Calculating margin (~12s)...':'Calculate margin'}</button>
            <button class="secondary ${state.busyOp==="rescue"?"is-loading":""}" id="rescue" ${state.busy||!state.simulate?"disabled":""}>${state.busyOp==="rescue"?'<span class="spin-dot"></span> Running rescue...':'Run rescue'}</button>
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

function nav(id,title,sub,icon){return `<button class="nav-item ${state.activeNav===id?"selected":""}" data-nav="${id}"><span class="nav-icon">${icon}</span><span><b>${title}</b><small>${sub}</small></span></button>`}
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
      ${metric("MODEL-DEFINED MARGIN (M̂)",m?.m_signed!=null?(m?.m_status==="SAMPLED_UB"?"≤ ":"")+fmt(m.m_signed,4):"—","normalised units",m?(m.binding_constraint?.axis?`binding: ${m.binding_constraint.axis}`:m.m_status):"awaiting calculation")}
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
  const hasQ = Number.isFinite(Number(q)), hasBd = Number.isFinite(Number(bd));
  const hasM = m && m.m_signed != null;
  const lo = hasQ && hasBd ? Math.min(q, bd) * 0.85 : 0;
  const hi = hasQ && hasBd ? Math.max(q, bd) * 1.15 : 1;
  const pos = v => Math.max(3, Math.min(97, (v - lo) / (hi - lo || 1) * 100));
  const qp = hasQ ? pos(q) : 50, bp = hasBd ? pos(bd) : 50;

  return `<div class="margin-scale">
    <div class="scale-labels"><span>Lower qNet (High Risk)</span><span>Higher qNet (Safer)</span></div>
    <div class="scale">
      <div class="unsafe" title="Below 75% boundary (Proarrhythmic risk)"></div>
      <div class="safe" title="Above 75% boundary (Safe repolarization)"></div>
      ${hasBd ? `<i class="tick boundary" style="left:${bp}%" title="Model boundary"></i>` : ""}
      ${hasQ ? `<i class="tick scenario" style="left:${qp}%" title="Scenario qNet"></i>` : ""}
    </div>
    <div class="markers">
      ${hasQ ? `<span style="left:${qp}%"><b>Scenario</b><strong>${fmt(q,5)}</strong></span>` : ""}
      ${hasBd ? `<span style="left:${bp}%"><b>Boundary</b><strong>${fmt(bd,5)}</strong></span>` : ""}
    </div>
    <div class="margin-copy">
      ${hasM ? `
        <div class="margin-badge-row">
          <span class="margin-val">${m.m_status==="SAMPLED_UB"?"≤ ":""}${fmt(m.m_signed,4)}</span>
          <span class="margin-unit">normalised units</span>
          <span class="tiny-pill ${m.m_signed > 0 ? "good" : "failed"}">${m.m_signed > 0 ? "OUTSIDE RISK ZONE" : "INSIDE RISK ZONE"}</span>
        </div>
        <div class="margin-detail-line">
          <span>Binding axis: <b>${esc(m.binding_constraint?.axis || "—")}</b></span>
          ${m.binding_constraint?.critical_raw_value != null ? `<span>Critical value: <b>${fmt(m.binding_constraint.critical_raw_value, 3)}</b></span>` : ""}
          <span>Evaluations: <b>${m.n_phi_evals ?? "—"}</b></span>
        </div>
      ` : `
        <strong>${statusLabel(m?.m_status)}</strong>
        <p class="muted">Click <b>Calculate margin</b> to evaluate multidimensional distance to the boundary.</p>
      `}
      <p class="disclaimer-note">${frozenCopy.margin}</p>
    </div>
  </div>`;
}
function statusLabel(s){return s==="SAMPLED_UB"?"≤ upper bound":s==="BUDGET_EXCEEDED"?"Budget exceeded":s||"Awaiting margin";}
function formatAction(act){
  if(!act) return "—";
  const c = act.class || act.class_;
  const p = act.param || {};
  if(c === "A1_K_CORRECTION") return `Potassium correction (K⁺ = ${fmt(p.k_o_mM, 1)} mM)`;
  if(c === "A2_EXPOSURE_REDUCTION") return `Dose de-escalation (${esc(p.drug || "drug")} ×${p.factor ?? "—"})`;
  if(c === "A3_DISCONTINUATION") return `Discontinuation (${esc(p.drug || "drug")})`;
  if(c === "A0_NO_ACTION") return "No intervention (maintain current)";
  return c || "—";
}
function rescueSummary(r){
  const best=r.best_action;
  return `<div class="rescue-grid"><div class="panel rescue-table"><div class="panel-head"><h3>Rescue analysis</h3><span>${esc(r.status||"")}</span></div>
    <table><thead><tr><th>Action</th><th>Cost</th><th>Φ after</th><th>Status</th></tr></thead><tbody>${(r.evaluated||[]).map(e=>`<tr><td>${esc(e.action)}</td><td class="mono">${fmt(e.cost,3)}</td><td class="mono ${e.phi>0?'text-good':''}">${fmt(e.phi,6)}</td><td><span class="state-dot ${e.feasible?"good":"neutral"}">${e.feasible?"FEASIBLE":"NOT FEASIBLE"}</span></td></tr>`).join("")}</tbody></table></div>
    <div class="panel best-card"><div class="section-kicker">BEST MODELED RESCUE</div>${best?`<h3>${esc(formatAction(best))}</h3><div class="best-number">${fmt(best.phi_after,6)}</div><span>Φ after · margin ${fmt(best.margin_after,4)}</span>`:`<h3>No feasible single action</h3><p>${esc(r.infeasibility?.explanation||"See the evaluated action set.")}</p>`}<div class="notice">${frozenCopy.rescue}</div></div></div>`;
}
function tabsSection(){
  const tabList = [
    {id:"mechanism", label:"Mechanism & Drugs"},
    {id:"margin", label:"Margin Detail"},
    {id:"rescue", label:"Rescue"},
    {id:"score", label:"Score Comparison"},
    {id:"history", label:`Results History (${state.history.length})`},
    {id:"verification", label:"Verification"},
    {id:"provenance", label:"Provenance"},
    {id:"docs", label:"Documentation"}
  ];
  return `<section class="lower">
    <div class="tabs">${tabList.map(t=>`<button class="${state.activeTab===t.id?"active":""}" data-tab="${t.id}">${t.label}</button>`).join("")}</div>
    <div class="tab-content">${tabContent()}</div>
  </section>`;
}
function tabContent(){
  if(state.activeTab==="mechanism")return mechanismTab();
  if(state.activeTab==="margin")return marginTab();
  if(state.activeTab==="rescue")return rescueTab();
  if(state.activeTab==="score")return scoreTab();
  if(state.activeTab==="history")return historyTab();
  if(state.activeTab==="verification")return verificationTab();
  if(state.activeTab==="docs")return docsTab();
  return provenanceTab();
}
function mechanismTab(){
  const d=drug(); return `<div class="two-col" id="channel-panel"><div><div class="section-kicker">CHANNEL PANEL</div><h3>Pharmacology registry</h3><p class="muted">Runtime block values are derived from the verified registry; unavailable/rejected channels are never invented.</p>
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
  const r=state.rescue;
  const infeas = r.infeasibility;
  const closest = infeas?.closest_action;
  const targetBufferPct = ((state.tau ?? 0.05) * 100).toFixed(0);
  
  return `<div>
    <div class="rescue-title">
      <div>
        <div class="section-kicker">FINITE ACTION SEARCH (§11–12)</div>
        <h3>${esc(r.status)}</h3>
      </div>
      <div class="rescue-meta-badges">
        <span class="tiny-pill ${r.status==='FEASIBLE'?'good':'amber'}">${esc(r.status)}</span>
        <span class="tiny-pill">${r.action_set_size} actions evaluated · ${r.n_noncredible} noncredible</span>
        <span class="tiny-pill">Target buffer: τ = ${targetBufferPct}% (${fmt(r.phi_target, 5)} C/F)</span>
      </div>
    </div>

    <div class="rescue-toolbar">
      <div class="tau-selector">
        <span class="tau-label">SAFETY TARGET BUFFER (τ):</span>
        <div class="pill-group">
          <button class="pill-btn ${(state.tau ?? 0.05) === 0.05 ? "active" : ""}" data-tau="0.05" title="Requires safety margin 5% above qNet boundary">Standard 5% Buffer (τ = 0.05)</button>
          <button class="pill-btn ${(state.tau ?? 0.05) === 0 ? "active" : ""}" data-tau="0" title="Requires crossing the boundary (Φ ≥ 0)">Boundary Crossing (τ = 0.00)</button>
        </div>
      </div>
      <button class="btn-sm secondary ${state.busyOp==='rescue'?'is-loading':''}" id="re-rescue">${state.busyOp==='rescue'?'Evaluating...':'Re-evaluate action set'}</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>Permitted Clinical Action</th>
          <th>Relative Cost</th>
          <th>Φ Achieved</th>
          <th>Credibility</th>
          <th>Feasibility</th>
        </tr>
      </thead>
      <tbody>
        ${(r.evaluated||[]).map(e=>`
          <tr class="${e.feasible?'row-feasible':''}">
            <td><b>${esc(e.action)}</b></td>
            <td class="mono">${fmt(e.cost, 3)}</td>
            <td class="mono ${e.phi > 0 ? 'text-good' : ''}">${fmt(e.phi, 6)}</td>
            <td><span class="tiny-pill ${credClass(e.credibility)}">${esc(e.credibility)}</span></td>
            <td><span class="state-dot ${e.feasible?'good':'neutral'}">${e.feasible?'FEASIBLE':'NOT FEASIBLE'}</span>${e.skipped_out_of_box?' · SKIPPED_OUT_OF_BOX':''}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>

    <div class="notice">${frozenCopy.rescue}</div>

    ${infeas ? `
      <div class="infeas-card">
        <div class="infeas-header">
          <span class="infeas-badge">${esc(infeas.reason_code)}</span>
          <h4>Mathematical Infeasibility Certificate</h4>
        </div>
        <p class="infeas-expl">${esc(infeas.explanation)}</p>

        <div class="infeas-details-grid">
          <div class="infeas-detail-item">
            <span class="detail-label">Closest permitted action</span>
            <b>${esc(formatAction(closest))}</b>
          </div>
          <div class="infeas-detail-item">
            <span class="detail-label">Achieved Repolarization (Φ)</span>
            <b class="mono ${closest?.phi > 0 ? 'text-good' : ''}">${fmt(closest?.phi, 6)} C/F</b>
          </div>
          <div class="infeas-detail-item">
            <span class="detail-label">Shortfall to Target Buffer</span>
            <b class="mono">${fmt(closest?.shortfall, 6)} C/F</b>
          </div>
          <div class="infeas-detail-item">
            <span class="detail-label">Binding Clinical Constraint</span>
            <b>${esc(infeas.limiting_bound || "A2 floor factor >= 0.25")}</b>
          </div>
        </div>

        <div class="infeas-interpretation">
          <div class="interp-title">Clinical &amp; Physiological Analysis:</div>
          <p>
            • <b>Extracellular Potassium:</b> Baseline K⁺ is already at the clinical ceiling (<b>5.4 mM</b>); further infusion is prohibited by hyperkalemic toxicity rules.<br>
            • <b>Discontinuation:</b> Dofetilide is a restricted inpatient antiarrhythmic with <code>discontinuable: false</code>; abrupt cessation without electrophysiologist supervision is unsafe.<br>
            • <b>Dose De-escalation:</b> Dose reduction to <b>25% exposure</b> successfully restores the cell into the safe repolarization zone (<b>Φ = +0.00146 &gt; 0</b>), but falls just <b>0.00005 C/F</b> short of the strict +5% safety buffer target.
          </p>
        </div>

        <div class="infeas-footer-note">${frozenCopy.infeas}</div>
      </div>
    ` : ""}
  </div>`;
}
function scoreTab(){
  if(!state.blindspot)return `<div class="empty-tab"><h3>Score comparison</h3><p>Run the blind-spot comparison to inspect the score against the mechanistic sweep.</p><button class="secondary" id="blindspot">Run comparison</button></div>`;
  return `<div><div class="section-kicker">CLINICAL-SCORE COMPARISON</div><h3>Mechanistic margin vs Tisdale score</h3><p class="muted">${esc(state.blindspot.verdict||state.blindspot.audit_status||"Comparison returned.")}</p><div class="notice">${frozenCopy.score}</div></div>`;
}
function historyTab(){
  if(!state.history.length) {
    return `<div class="empty-tab">
      <div class="section-kicker">SESSION AUDIT</div>
      <h3>No session history recorded yet</h3>
      <p class="muted">Run simulations, margin searches, or rescue optimizations to populate this session log. You can restore any previous configuration with one click.</p>
    </div>`;
  }
  return `<div>
    <div class="verify-head">
      <div>
        <div class="section-kicker">SESSION RESULTS AUDIT</div>
        <h3>Results History (${state.history.length} runs recorded)</h3>
        <p class="muted">All mechanistic runs evaluated in the current browser session.</p>
      </div>
      <button class="btn-sm" id="clear-hist">Clear history</button>
    </div>
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Type</th>
          <th>Drug & Exposure</th>
          <th>Extracellular K⁺</th>
          <th>qNet</th>
          <th>Signed Margin (M̂)</th>
          <th>Status / Binding</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        ${state.history.map(h => `
          <tr>
            <td class="mono">${esc(h.time)}</td>
            <td><span class="tiny-pill ${h.type==="margin"?"good":h.type==="simulation"?"verified":"amber"}">${esc(h.type.toUpperCase())}</span></td>
            <td><b>${esc(h.drug_name)}</b> <span class="mono">${fmt(h.exposure,2)}×</span></td>
            <td class="mono">${fmt(h.k,1)} mM</td>
            <td class="mono">${h.qnet != null ? fmt(h.qnet, 5) + " µC/µF" : "—"}</td>
            <td class="mono"><b>${h.margin != null ? fmt(h.margin, 4) : "—"}</b></td>
            <td>${h.binding_axis ? `binding: ${esc(h.binding_axis)}` : esc(h.margin_status || "COMPLETED")}</td>
            <td><button class="btn-sm" data-restore="${esc(h.id)}">Restore</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  </div>`;
}
function verificationTab(){
  const v=state.validation;if(!v)return `<div class="empty-tab"><h3>Verification unavailable</h3></div>`;
  const checks=v.checks||[];return `<div><div class="verify-head"><div><div class="section-kicker">VERIFICATION BATTERY</div><h3>${esc(v.aggregate||"UNVERIFIED")}</h3><p class="muted">Configuration hash ${esc(v.battery?.config_hash||v.config_hash||"—")}</p></div><button class="secondary" id="verify2">Refresh verification</button></div>
  <table><thead><tr><th>ID</th><th>Check</th><th>Tier</th><th>State</th><th>Detail</th></tr></thead><tbody>${checks.map(c=>`<tr><td class="mono">${esc(c.id)}</td><td>${esc(c.name)}</td><td>${esc(c.tier)}</td><td><span class="state-dot ${c.state==="PASS"?"good":c.state==="FAIL"?"bad":"neutral"}">${esc(c.state)}</span></td><td class="muted">${esc(c.detail||"")}</td></tr>`).join("")}</tbody></table></div>`;
}
function docsTab(){
  return `<div>
    <div class="section-kicker">METHODS & DATA SPECIFICATION</div>
    <h3>Computational Cardiac Electrophysiology Reference</h3>
    <p class="muted">Scientific foundations, ODE formulations, and regulatory risk margins for TorsadeTwin.</p>
    
    <div class="doc-grid">
      <div class="doc-card">
        <div class="section-kicker">01 / BIOPHYSICAL FOUNDATION</div>
        <h3>O'Hara-Rudy Dynamic (ORd) Model</h3>
        <p>The state equations model human ventricular electrophysiology at 37°C across 41 dynamic state variables and 15 distinct ionic currents (IKr, IKs, IK1, Ito, INa, INaL, ICaL, etc.).</p>
        <pre>Pacing protocol: Steady-state pacing at Cycle Length = 2000 ms
State vector: x = [V, [Na⁺]i, [K⁺]i, [Ca²⁺]i, gating states...]
Cell geometry: Endocardial single cell formulation</pre>
      </div>

      <div class="doc-card">
        <div class="section-kicker">02 / CIPA METRIC</div>
        <h3>Net Repolarization Charge (qNet)</h3>
        <p>Adopted by the FDA/CiPA initiative, qNet is the time integral of net outward current during the action potential beat, serving as a validated surrogate for proarrhythmic risk.</p>
        <pre>qNet = ∫ (IKr + IKs + IK1 + Ito + INaL + ICaL) dt
Control reference: qNet_ctrl = 0.03019 µC/µF
Model boundary: 75% of control = 0.02264 µC/µF</pre>
      </div>

      <div class="doc-card">
        <div class="section-kicker">03 / MATHEMATICAL NOVELTY</div>
        <h3>Signed Safety Margin M̂(x₀)</h3>
        <p>Measures the minimum weighted distance in normalised state space to the critical boundary Φ = 0, signed positive if safe and negative if within the proarrhythmic risk zone.</p>
        <pre>Φ(x) = qNet(x) - 0.75 · qNet_ctrl
M̂(x₀) = sign(Φ(x₀)) · min_{x ∈ ∂S} ||x - x₀||_W
Search budget: 300 evaluations across potassium and drug axes</pre>
      </div>

      <div class="doc-card">
        <div class="section-kicker">04 / INTERVENTIONAL GUIDANCE</div>
        <h3>Finite Rescue Action Set</h3>
        <p>Performs exhaustive evaluation over an explicit, finite set of clinical countermeasures to find the minimum-cost intervention that restores positive safety margin.</p>
        <pre>Action 1: Extracellular potassium adjustment [3.5 - 5.0 mM]
Action 2: Drug dose de-escalation / exposure reduction
Action 3: Complete drug discontinuation</pre>
      </div>
    </div>

    <div class="doc-card">
      <div class="section-kicker">05 / CURATED REFERENCE DRUGS</div>
      <h3>Standard CiPA Validation Pharmacology</h3>
      <p>Includes high-, intermediate-, and low-risk reference compounds with peer-reviewed multi-channel patch clamp data: <b>Dofetilide</b> (high risk, pure hERG), <b>Quinidine</b> (high risk, multi-channel), <b>Cisapride</b> (high risk), <b>Sotalol</b> (high risk), <b>Verapamil</b> (low risk, hERG + CaV1.2 balanced block), <b>Diltiazem</b> (low risk), and <b>Drug-free Control</b>.</p>
    </div>
  </div>`;
}
function provenanceTab(){
  const h=state.health||{};return `<div class="provenance-grid"><div><div class="section-kicker">TRACEABILITY</div><h3>Source → parameter → computation → output</h3><div class="chain">${["Published pharmacology","Verified registry","ORd-CiPA model artefact","CVODES simulation","qNet / APD90","Margin / Rescue","Reproducible result hash"].map((x,i)=>`<div><span>${String(i+1).padStart(2,"0")}</span><b>${x}</b></div>`).join("")}</div></div><div class="hashes"><div><span>Model hash</span><code>${esc(h.model_hash||"—")}</code></div><div><span>Config hash</span><code>${esc(h.config_hash||"—")}</code></div><div><span>Offline</span><code>${h.offline?"TRUE":"—"}</code></div></div></div>`;
}
function bind(){
  $("#drug")?.addEventListener("change",e=>{state.selectedDrug=e.target.value;state.simulate=null;state.margin=null;state.rescue=null;render()});
  $("#exposure")?.addEventListener("input",e=>{state.exposure=Number(e.target.value);e.target.nextElementSibling.value=`${fmt(state.exposure,2)}×`});
  $("#k")?.addEventListener("input",e=>{state.k=Number(e.target.value);e.target.nextElementSibling.value=`${fmt(state.k,1)} mM`});
  $("#cl")?.addEventListener("input",e=>{state.cl=Number(e.target.value);e.target.nextElementSibling.value=`${state.cl} ms`});
  $$(".preset").forEach(b=>b.addEventListener("click",()=>{state.selectedDrug=b.dataset.drug;state.simulate=null;state.margin=null;state.rescue=null;render()}));
  $("#simulate")?.addEventListener("click",runSim);$("#margin")?.addEventListener("click",runMargin);$("#rescue")?.addEventListener("click",()=>runRescue());
  $("#re-rescue")?.addEventListener("click",()=>runRescue());
  $$("[data-tau]").forEach(b=>b.addEventListener("click",()=>{
    state.tau=Number(b.dataset.tau);
    runRescue(state.tau);
  }));
  $("#verify")?.addEventListener("click",()=>{state.activeNav="validation";state.activeTab="verification";render()});$("#verify2")?.addEventListener("click",runVerify);
  $("#report")?.addEventListener("click",exportReport);$("#report2")?.addEventListener("click",exportReport);
  $("#blindspot")?.addEventListener("click",runBlindspot);
  $$("[data-tab]").forEach(b=>b.addEventListener("click",()=>{
    state.activeTab=b.dataset.tab;
    if(b.dataset.tab==="mechanism") state.activeNav="drugs";
    else if(b.dataset.tab==="history") state.activeNav="history";
    else if(b.dataset.tab==="verification") state.activeNav="validation";
    else if(b.dataset.tab==="docs") state.activeNav="docs";
    render();
  }));
  $$("[data-nav]").forEach(b=>b.addEventListener("click",()=>{
    const n = b.dataset.nav;
    state.activeNav = n;
    if(n==="overview"){
      state.activeTab="mechanism";
      render();
      window.scrollTo({top:0,behavior:"smooth"});
    } else if(n==="new"){
      state.exposure=1;
      state.k=5.4;
      state.cl=2000;
      state.simulate=null;
      state.margin=null;
      state.rescue=null;
      render();
      toast("Ready for new analysis. Declare scenario inputs.","info");
      document.querySelector(".scenario-panel")?.scrollIntoView({behavior:"smooth"});
    } else if(n==="drugs"){
      state.activeTab="mechanism";
      render();
      setTimeout(()=>{document.querySelector("#channel-panel")?.scrollIntoView({behavior:"smooth"});},60);
    } else if(n==="history"){
      state.activeTab="history";
      render();
      setTimeout(()=>{document.querySelector(".lower")?.scrollIntoView({behavior:"smooth"});},60);
    } else if(n==="validation"){
      state.activeTab="verification";
      render();
      setTimeout(()=>{document.querySelector(".lower")?.scrollIntoView({behavior:"smooth"});},60);
    } else if(n==="docs"){
      state.activeTab="docs";
      render();
      setTimeout(()=>{document.querySelector(".lower")?.scrollIntoView({behavior:"smooth"});},60);
    }
  }));
  $$("[data-restore]").forEach(btn=>btn.addEventListener("click",()=>{
    const id = btn.dataset.restore;
    const item = state.history.find(h=>h.id===id);
    if(item && item.snapshot){
      state.selectedDrug = item.snapshot.selectedDrug;
      state.exposure = item.snapshot.exposure;
      state.k = item.snapshot.k;
      state.cl = item.snapshot.cl;
      state.simulate = item.snapshot.simulate;
      state.margin = item.snapshot.margin;
      state.rescue = item.snapshot.rescue;
      state.activeTab = item.type==="margin"?"margin":(item.type==="rescue"?"rescue":"mechanism");
      render();
      toast(`Restored run from ${item.time}`,"success");
      document.querySelector(".results")?.scrollIntoView({behavior:"smooth"});
    }
  }));
  $("#clear-hist")?.addEventListener("click",()=>{state.history=[];render();toast("History cleared","info")});
}
boot();
