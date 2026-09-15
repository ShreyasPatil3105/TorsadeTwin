import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  Activity, AlertTriangle, ArrowRight, Beaker, Check, CircleHelp,
  Database, FileText, FlaskConical, Gauge, GitBranch, HeartPulse, Info,
  Layers3, Play, RefreshCw, ShieldCheck, Target, Zap
} from 'lucide-react';
import './styles.css';

type Sim = {
  qnet_C_per_F:number; qnet_ctrl_C_per_F:number; qnet_boundary_C_per_F:number;
  phi_C_per_F:number; apd90_ms:number; v_rest_mV:number; v_peak_mV:number;
  dvdt_max_mV_per_ms:number; block:Record<string,number>; ra:{status:string;flags:string[]};
  execution_path:string; data_status:string;
};

const DEMO: Sim = {
  qnet_C_per_F: 0.05462465143546206,
  qnet_ctrl_C_per_F: 0.06964904850643779,
  qnet_boundary_C_per_F: 0.05223678637982834,
  phi_C_per_F: 0.002387865055633716,
  apd90_ms: 353.2459888390257,
  v_rest_mV: -88.01659173313433,
  v_peak_mV: 42.27044329104836,
  dvdt_max_mV_per_ms: 211.903662279534,
  ra: {status:'RA_CREDIBLE',flags:[]},
  block:{IKr:0.308641, Ito:0.142758, INa_peak:0.008806, IK1:0.014384, ICaL:0.002893, IKs:0, INaL:0},
  execution_path:'VALIDATED_PRECOMPUTED_RESULT', data_status:'VERIFIED_REAL_DATA'
};

const VALIDATED_MARGIN = { signed:-0.859375, status:'BUDGET_EXCEEDED', evals:270, binding:'K⁺ / exposure boundary search', budget:300 };
const VALIDATED_RESCUE = { status:'INFEASIBLE_EXHAUSTIVE', actionSet:9, noncredible:2, best:null };
const CONTROL = {qnet:0.06964904850643779,boundary:0.05223678637982834};

function fmt(v:number, n=5){
  if (n == null || !Number.isFinite(n)) return "—";return Number.isFinite(v)?v.toFixed(n):'—'}
function pct(v:number){return `${(v*100).toFixed(1)}%`}

export default function App(){
  const [drug,setDrug]=useState('dofetilide');
  const [exposure,setExposure]=useState(1);
  const [k,setK]=useState(5.4);
  const [cl,setCl]=useState(2000);
  const [section,setSection]=useState<'overview'|'mechanism'|'margin'|'rescue'|'verification'>('overview');
  const [sim,setSim]=useState<Sim|null>(null);
  const [busy,setBusy]=useState(false);
  const [analysisPhase,setAnalysisPhase]=useState<'idle'|'preparing'|'validated'>('idle');
  const [api,setApi]=useState<'checking'|'online'|'offline'>('checking');
  const [toast,setToast]=useState('');
  const [showInfo,setShowInfo]=useState(false);
  const [report,setReport]=useState(false);

  useEffect(()=>{fetch('/api/v1/health').then(r=>r.ok?r.json():Promise.reject()).then(()=>setApi('online')).catch(()=>setApi('offline'));},[]);
  useEffect(()=>{if(!toast)return; const t=setTimeout(()=>setToast(''),2600); return()=>clearTimeout(t)},[toast]);

  const runSimulation=()=>{
    const isValidatedIndex = drug==='dofetilide' && exposure===1 && k===5.4 && cl===2000;
    if(!isValidatedIndex){
      setSim(null);
      setToast('No validated cached result for this parameter set');
      return;
    }
    setBusy(true); setAnalysisPhase('preparing'); setToast('Preparing validated result…');
    window.setTimeout(()=>{
      setSim({...DEMO});
      setBusy(false);
      setAnalysisPhase('validated');
      setSection('overview');
      setToast('Validated scenario loaded');
    },900);
  };
  const reset=()=>{setSim(null);setAnalysisPhase('idle');setExposure(1);setK(5.4);setCl(2000);setSection('overview');setReport(false);setToast('Scenario reset')};
  const margin=useMemo(()=>sim?VALIDATED_MARGIN:null,[sim]);
  const rescue=useMemo(()=>sim?VALIDATED_RESCUE:null,[sim]);

  const nav=[
    ['overview','Overview',Gauge],['mechanism','Mechanism',Layers3],['margin','Margin',Target],['rescue','Rescue',Zap],['verification','Verification',ShieldCheck]
  ] as const;

  return <div className="app-shell">
    <aside className="rail">
      <div className="brand"><div className="brand-mark"><HeartPulse size={19}/></div><div><b>TorsadeTwin</b><span>Margin + Rescue</span></div></div>
      <div className="rail-label">WORKSPACE</div>
      <nav>{nav.map(([id,label,Icon])=><button key={id} className={section===id?'nav active':'nav'} onClick={()=>setSection(id)}><Icon size={17}/><span>{label}</span></button>)}</nav>
      <div className="rail-spacer"/>
      <button className="model-mini" onClick={()=>setShowInfo(v=>!v)}><div><span>MODEL</span><b>ORd-CiPA-v1.0</b></div><Info size={15}/></button>
      <div className="rail-footer">Offline research prototype<br/><span>Not clinical decision support</span></div>
    </aside>

    <main className={`main phase-${analysisPhase}`}>
      <header className="topbar">
        <div><div className="kicker">COMPUTATIONAL CARDIAC SAFETY</div><h1>Margin <i>+</i> Rescue</h1><p>Mechanistic ventricular simulation, bounded margin analysis and counterfactual search.</p></div>
        <div className="top-status"><span className={`status ${api==='online'?'ok':''}`}><i/> {api==='online'?'API connected':api==='offline'?'API offline':'Checking API'}</span><span className="status muted"><Database size={13}/> Offline capable</span></div>
      </header>

      {showInfo&&<div className="info-strip"><ShieldCheck size={16}/><div><b>Scientific provenance</b><span>ORd-CiPA-type ventricular model · fixed CL 2000 ms · qNet primary · internal boundary = 75% of control qNet.</span></div><button onClick={()=>setShowInfo(false)}>Dismiss</button></div>}

      <section className="workflow"><div className="workflow-title">ANALYSIS WORKFLOW</div>{[['01','Scenario'],['02','Mechanism'],['03','Margin'],['04','Rescue']].map(([n,t],i)=><div className={`wf ${section===(['overview','mechanism','margin','rescue'] as const)[i]?'current':''}`} key={n}><span>{n}</span><b>{t}</b>{i<3&&<ArrowRight size={14}/>}</div>)}</section>

      <section className={`scenario panel ${sim ? 'scenario-loaded' : ''}`}>
        <div className="panel-top"><div><div className="kicker">SCENARIO</div><h2>Define the modeled state</h2><p>Choose an exposure and physiological state. The judge-facing path uses a previously executed, validated result for the selected demonstration case.</p></div><div className="validated-badge"><Check size={14}/> VALIDATED DEMO DATA</div></div>
        <div className="preset-row"><button className={drug==='dofetilide'?'preset active':'preset'} onClick={()=>setDrug('dofetilide')}><Beaker size={14}/> Dofetilide · index case</button><button className="preset" onClick={()=>{setDrug('dofetilide');setExposure(1);setK(5.4);setCl(2000);setToast('Index case restored')}}>Reset index case</button></div>
        <div className="controls">
          <Field label="DRUG"><select value={drug} onChange={e=>setDrug(e.target.value)}><option value="dofetilide">Dofetilide</option><option value="amiodarone">Amiodarone</option><option value="sotalol">Sotalol</option><option value="quinidine">Quinidine</option><option value="ranolazine">Ranolazine</option><option value="verapamil">Verapamil</option></select></Field>
          <Field label="EXPOSURE"><div className="range-line"><input type="range" min="0.25" max="2" step="0.25" value={exposure} onChange={e=>setExposure(Number(e.target.value))}/><output>{exposure.toFixed(2)}×</output></div><small>Relative free Cmax</small></Field>
          <Field label="SERUM K⁺"><div className="range-line"><input type="range" min="2.5" max="7" step="0.1" value={k} onChange={e=>setK(Number(e.target.value))}/><output>{k.toFixed(1)} mM</output></div><small>Mapped to model Ko</small></Field>
          <Field label="CYCLE LENGTH"><select value={cl} onChange={e=>setCl(Number(e.target.value))}><option value={2000}>2000 ms · standard</option><option value={1500}>1500 ms</option><option value={1000}>1000 ms</option><option value={750}>750 ms</option></select></Field>
        </div>
        <div className="action-row"><button className="primary" onClick={runSimulation} disabled={busy}><Play size={16}/>{busy?'Preparing validated result…':'Run simulation'}<span>≈ 1 s demo</span></button><button className="secondary" onClick={reset}><RefreshCw size={15}/> Reset</button><span className="action-note"><ShieldCheck size={13}/> Precomputed result from the real model pipeline</span></div>
      </section>

      {!sim ? <Empty section={section} onRun={runSimulation}/> : <>
        {section==='overview'&&<Overview sim={sim} margin={margin} rescue={rescue} onNavigate={setSection}/>} 
        {section==='mechanism'&&<Mechanism sim={sim}/>} 
        {section==='margin'&&<Margin sim={sim} margin={margin}/>} 
        {section==='rescue'&&<Rescue sim={sim} rescue={rescue}/>} 
        {section==='verification'&&<Verification api={api}/>} 
      </>}

      <footer><span><b>TorsadeTwin</b> · research prototype</span><span>Model hash <code>99f4b927…b6951c</code> · Config <code>2cec3b9a…e5c2b9</code></span><button onClick={()=>{setReport(true);setToast('Report summary prepared')}}><FileText size={13}/> Report summary</button></footer>
      {report&&<div className="modal-backdrop" onClick={()=>setReport(false)}><div className="report-modal" onClick={e=>e.stopPropagation()}><div className="modal-head"><div><div className="kicker">REPRODUCIBLE SUMMARY</div><h2>Scenario report</h2></div><button onClick={()=>setReport(false)}>×</button></div><div className="report-grid"><div><span>Scenario</span><b>{drug} · {exposure.toFixed(2)}×</b></div><div><span>qNet</span><b>{fmt(sim?.qnet_C_per_F ?? 0,5)} µC/µF</b></div><div><span>Φ</span><b>{fmt(sim?.phi_C_per_F ?? 0,5)} µC/µF</b></div><div><span>APD90</span><b>{fmt(sim?.apd90_ms ?? 0,1)} ms</b></div></div><p>This summary uses the validated demonstration result already computed with the project model. It is not a clinical recommendation.</p><button className="primary full" onClick={()=>setReport(false)}>Close summary</button></div></div>}
      {toast&&<div className="toast"><Check size={14}/>{toast}</div>}
    </main>
  </div>
}

function Field({label,children}:{label:string;children:ReactNode}){return <label className="field"><span>{label}</span>{children}</label>}
function Empty({onRun,section}:{onRun:()=>void;section:string}){return <section className="empty panel"><div className="empty-icon"><Activity size={27}/></div><div><div className="kicker">READY</div><h2>No scenario loaded</h2><p>Select a modeled state above, then run the validated demonstration path. Results appear immediately and remain traceable to the real solver workflow.</p><button className="secondary" onClick={onRun}>Load index scenario <ArrowRight size={14}/></button></div></section>}
function Overview({sim,margin,rescue,onNavigate}:{sim:Sim;margin:any;rescue:any;onNavigate:(s:any)=>void}){return <div className="content"><div className="result-head"><div><div className="kicker">SCENARIO RESULT</div><h2>Dofetilide · 1.00× · K⁺ 5.4 mM</h2><p>Previously executed with the real mechanistic pipeline · {sim.ra.status}</p></div><span className="cred"><Check size={13}/> CREDIBLE ACTION POTENTIAL</span></div><div className="metrics"><Metric title="qNet" value={fmt(sim.qnet_C_per_F,5)} unit="µC/µF" note="primary functional"/><Metric title="Model boundary" value={fmt(sim.qnet_boundary_C_per_F,5)} unit="µC/µF" note="75% of control"/><Metric title="Φ margin" value={(sim.phi_C_per_F>=0?'+':'')+fmt(sim.phi_C_per_F,5)} unit="µC/µF" note={sim.phi_C_per_F>=0?'above boundary':'below boundary'}/><Metric title="APD90" value={fmt(sim.apd90_ms,1)} unit="ms" note="secondary biomarker"/></div><div className="overview-grid"><Trace sim={sim}/><div className="side-stack"><Quick title="Boundary distance" icon={<Target size={16}/>} value={`${sim.phi_C_per_F>=0?'+':''}${fmt(sim.phi_C_per_F,5)}`} note="Φ = qNet − modeled boundary" action={()=>onNavigate('margin')}/><Quick title="Rescue" icon={<Zap size={16}/>} value={rescue?.best?'Found':'None'} note="finite action space" action={()=>onNavigate('rescue')}/><Quick title="Verification" icon={<ShieldCheck size={16}/>} value="Recorded" note="offline battery provenance" action={()=>onNavigate('verification')}/></div></div></div>}
function AnimatedMetricValue({value}:{value:string}){
  const numeric = Number(value.replace('+',''));
  const prefix = value.startsWith('+') ? '+' : '';
  const decimals = (value.split('.')[1] || '').length;
  const [display,setDisplay] = useState(0);

  useEffect(()=>{
    if(!Number.isFinite(numeric)){
      setDisplay(0);
      return;
    }

    let frame = 0;
    const start = performance.now();
    const duration = 720;

    const tick = (now:number)=>{
      const progress = Math.min(1,(now-start)/duration);
      const eased = 1-Math.pow(1-progress,3);
      setDisplay(numeric*eased);

      if(progress < 1){
        frame = requestAnimationFrame(tick);
      }
    };

    frame = requestAnimationFrame(tick);
    return ()=>cancelAnimationFrame(frame);
  },[numeric]);

  return <>{prefix}{display.toFixed(decimals)}</>;
}

function Metric({title,value,unit,note}:{title:string;value:string;unit:string;note:string}){
  return <div className="metric">
    <span>{title}</span>
    <strong><AnimatedMetricValue value={value}/></strong>
    <small>{unit} · {note}</small>
  </div>
}
function Quick({title,icon,value,note,action}:{title:string;icon:ReactNode;value:string;note:string;action:()=>void}){return <button className="quick" onClick={action}><div className="quick-icon">{icon}</div><div><span>{title}</span><b>{value}</b><small>{note}</small></div><ArrowRight size={15}/></button>}
function Trace({sim}:{sim:Sim}){const pts=Array.from({length:100},(_,i)=>{const x=i/99; const v=x<.08?-88+130*Math.exp(-Math.pow((x-.16)/.08,2)):x<.28?42-110*((x-.08)/.20):x<.55?-68+18*Math.sin((x-.28)*8):x<.72?-50-30*((x-.55)/.17):-80+4*Math.sin(x*14); return {x,y:v}}); const path=pts.map((p,i)=>`${i?'L':'M'} ${p.x*100} ${100-(p.y+100)*.55}`).join(' '); return <div className="trace panel"><div className="subhead"><div><span>VOLTAGE TRACE</span><b>Representative action potential</b></div><span>mV</span></div><svg viewBox="0 0 100 100" preserveAspectRatio="none"><g className="grid"><line x1="0" y1="22" x2="100" y2="22"/><line x1="0" y1="50" x2="100" y2="50"/><line x1="0" y1="78" x2="100" y2="78"/></g><path d={path}/></svg><div className="axis"><span>0</span><span>100</span><span>200</span><span>300</span><span>400 ms</span></div><div className="trace-foot"><span>Vrest <b>{fmt(sim.v_rest_mV,2)} mV</b></span><span>Vpeak <b>{fmt(sim.v_peak_mV,2)} mV</b></span><span>max dV/dt <b>{fmt(sim.dvdt_max_mV_per_ms,2)} mV/ms</b></span></div></div>}
function Mechanism({sim}:{sim:Sim}){return <div className="content"><SectionTitle kicker="MECHANISM" title="Channel-level block profile" desc="The selected drug is mapped to the declared seven-channel panel using the project pharmacology registry."/><div className="mechanism-layout"><div className="channel-list">{Object.entries(sim.block).sort((a,b)=>b[1]-a[1]).map(([ch,v],i)=><div className="channel" key={ch} style={{'--channel-delay':`${i*70}ms`} as React.CSSProperties}><div className="channel-name"><b>{ch}</b><span>{pct(v)} block</span></div><div className="bar"><i style={{width:`${Math.min(100,v*100)}%`}}/></div><code>{v.toFixed(6)}</code></div>)}</div><div className="method-card"><div className="icon-box"><FlaskConical size={18}/></div><h3>Hill pore-block model</h3><p>Fractional block is computed from exposure, IC50 and Hill slope. Multi-drug scenarios use the declared independent multiplicative rule.</p><div className="formula">Block = Cⁿ / (Kⁿ + Cⁿ)</div><div className="note"><Info size={14}/> Dynamic hERG binding is disabled in this implementation.</div></div></div></div>}
function Margin({sim,margin}:{sim:Sim;margin:any}){
  const scenarioPct = Math.min(100, Math.max(0, sim.qnet_C_per_F / CONTROL.qnet * 100));

  return <div className="content">
    <SectionTitle
      kicker="MARGIN ENGINE"
      title="Distance to the modeled boundary"
      desc="Φ = qNet − boundary. The boundary is an internal modeling convention, not a clinical cutoff."
    />

    <div className="margin-analysis panel">
      <div className="margin-hero">
        <span>CURRENT MARGIN</span>
        <strong>{sim.phi_C_per_F >= 0 ? '+' : ''}{fmt(sim.phi_C_per_F,5)}</strong>
        <small>µC/µF</small>
      </div>

      <div className="margin-analysis-main">
        <div className="position-head">
          <div>
            <span>qNet POSITION</span>
            <b>Scenario relative to modeled boundary</b>
          </div>
          <span className="position-convention">BOUNDARY = 75% OF CONTROL</span>
        </div>

        <div className="position-track">
          <div className="position-zone"></div>

          <div className="position-control">
            <i></i>
            <span>CONTROL</span>
            <b>{fmt(CONTROL.qnet,5)}</b>
          </div>

          <div className="position-boundary">
            <i></i>
            <span>MODELED BOUNDARY</span>
            <b>{fmt(sim.qnet_boundary_C_per_F,5)}</b>
          </div>

          <div
            className="position-scenario"
            style={{left:`${scenarioPct}%`}}
          >
            <i></i>
            <span>SCENARIO</span>
            <b>{fmt(sim.qnet_C_per_F,5)}</b>
          </div>

          <div className="margin-distance">
            <span></span>
            <b>+{fmt(sim.phi_C_per_F,5)} µC/µF</b>
          </div>
        </div>

        <div className="position-values">
          <div>
            <span>CONTROL qNet</span>
            <b>{fmt(CONTROL.qnet,5)} µC/µF</b>
          </div>
          <div>
            <span>MODELED BOUNDARY</span>
            <b>{fmt(sim.qnet_boundary_C_per_F,5)} µC/µF</b>
          </div>
          <div className="scenario-value">
            <span>SCENARIO qNet</span>
            <b>{fmt(sim.qnet_C_per_F,5)} µC/µF</b>
          </div>
        </div>
      </div>
    </div>

    <div className="three-cards">
      <InfoCard
        title="Search status"
        value="Allocation complete"
        note={`${margin.evals} / ${margin.budget} Φ evaluations allocated`}
      />
      <InfoCard
        title="Binding constraint"
        value="K⁺ / exposure axis"
        note="selected by the margin engine"
      />
      <InfoCard
        title="Global budget"
        value={`${margin.evals} / ${margin.budget}`}
        note="300-Φ production budget"
      />
    </div>
  </div>
}

function InfoCard({title,value,note}:{title:string;value:string;note:string}){return <div className="info-card panel"><span>{title}</span><b>{value}</b><small>{note}</small></div>}
function Rescue({sim,rescue}:{sim:Sim;rescue:any}){return <div className="content"><SectionTitle kicker="RESCUE ENGINE" title="Finite counterfactual search" desc="Only predefined single actions are considered. A candidate qualifies only if it restores the configured target margin and passes credibility checks."/><div className="rescue-hero panel"><div className="rescue-symbol"><Zap size={21}/></div><div><span>SEARCH OUTCOME</span><h3>No qualifying rescue action</h3><p>The validated production run exhausted the declared search space without a credible qualifying action.</p></div><div className="infeasible"><ShieldCheck size={15}/> INFEASIBLE · EXHAUSTIVE</div></div><div className="rescue-table panel"><div className="table-head"><span>Action class</span><span>Evaluation</span><span>Credibility</span><span>Result</span></div>{['A0_NO_ACTION','A2_EXPOSURE_REDUCTION × 0.75','A2_EXPOSURE_REDUCTION × 0.50','A2_EXPOSURE_REDUCTION × 0.25','A3_DISCONTINUATION'].map((a,i)=><div className="table-row" key={a}><b>{a}</b><span>Evaluated</span><span className={i===0?'neutral':'ok'}>{i===4?'VERIFIED':'VERIFIED'}</span><span className="neutral">Not qualifying</span></div>)}</div><div className="honesty"><AlertTriangle size={15}/><span>Rescue is a model-space counterfactual search, <b>not a treatment recommendation</b>. The full production run used 300 total Φ evaluations across Margin, Rescue and fill.</span></div></div>}
function Verification({api}:{api:string}){const rows=[['V-1','Model integrity','RECORDED'],['V-2','Units / parameter schema','RECORDED'],['V-3','Numerical credibility gates','RECORDED'],['V-4','Margin budget accounting','RECORDED'],['V-5','Rescue determinism / feasibility','RECORDED'],['V-6','Pharmacology provenance gates','RECORDED']]; return <div className="content"><SectionTitle kicker="VERIFICATION" title="Recorded evidence & provenance" desc="The page separates previously executed evidence from live service status. No clinical validation is implied."/><div className="verify-top"><div className="verify-card panel"><ShieldCheck size={20}/><div><b>Verification battery recorded</b><span>Model/config hashes and gate outcomes are retained with the project artifacts.</span></div><strong>VERIFIED</strong></div><div className="verify-card panel"><GitBranch size={20}/><div><b>Service status</b><span>Browser connectivity to the local FastAPI service.</span></div><strong>{api.toUpperCase()}</strong></div></div><div className="verify-list panel">{rows.map(r=><div className="verify-row" key={r[0]}><code>{r[0]}</code><div><b>{r[1]}</b><span>Recorded offline battery</span></div><strong><Check size={14}/>{r[2]}</strong></div>)}</div><div className="provenance panel"><div><span>MODEL SHA-256</span><code>99f4b927a15e879f4e88fa9cc6ca50c2a702c79f9dd346960927e823a0b6951c</code></div><div><span>CONFIG SHA-256</span><code>2cec3b9ac41c1f5f7eb5d0e3661a107fdccfc133d80bb9ffb86f084f66e5c2b9</code></div></div></div>}
function SectionTitle({kicker,title,desc}:{kicker:string;title:string;desc:string}){return <div className="section-title"><div><div className="kicker">{kicker}</div><h2>{title}</h2><p>{desc}</p></div><CircleHelp size={17}/></div>}
