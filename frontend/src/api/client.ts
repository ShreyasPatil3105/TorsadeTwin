// API client — offline, local, deterministic. All responses carry provenance/credibility/hashes.
export interface DrugExposure {
  drug_id: string;
  exposure_multiplier: number;
}

export interface SimulateRequest {
  drugs: DrugExposure[];
  k_o_mM: number;
  cl_ms: number;
  cell_type?: string;
  solver_profile?: string;
  return_trace?: boolean;
  combo_rule?: string;
}

export interface SimulateResponse {
  qnet_C_per_F: number;
  qnet_ctrl_C_per_F: number;
  qnet_boundary_C_per_F: number;
  phi_C_per_F: number;
  apd90_ms: number | null;
  ra: { flags: string[]; status: string };
  block: Record<string, number>;
  credibility: { state: string; checks: Record<string, string> };
  tags: string[];
  trace?: { dt_ms: number; t_ms: number[]; v_mV: number[]; i_net_A_per_F: number[] };
}

export interface MarginResponse {
  phi_now: number;
  m_signed: number | null;
  m_status: string;
  m_label: string;
  axes: Array<{
    axis: string;
    distance: number | null;
    critical_raw_value: number | null;
    direction: string | null;
    monotonicity: string;
    all_roots: number[];
    reachable: boolean;
    sensitivity_share: number | null;
  }>;
  binding_constraint: {
    axis: string | null;
    critical_raw_value: number | null;
    tied_axes: string[];
    alternative_axis: string | null;
    alternative_critical_value: number | null;
    distance_vs_sensitivity_disagree: boolean;
  };
  n_phi_evals: number;
  unit_convention: string;
  credibility: { state: string };
  disclaimers: string[];
}

export interface RescueResponse {
  status: string;
  search_scope: string;
  phi_target: number;
  best_action: { class: string; param: Record<string, unknown>; cost: number; phi_after: number; margin_after?: number; credibility: string } | null;
  co_optimal: Array<Record<string, unknown>>;
  evaluated: Array<{ action: string; cost: number; phi: number; feasible: boolean; credibility: string }>;
  action_set_size: number;
  n_noncredible: number;
  infeasibility?: {
    reason_code: string;
    explanation: string;
    closest_action: Record<string, unknown>;
    shortfall_normalised: number | null;
    limiting_bound: string;
    what_would_help: string;
  };
  credibility: { state: string };
  disclaimers: string[];
}

export interface HealthResponse {
  status: string;
  model_id: string;
  model_hash: string | null;
  config_hash: string;
  data_integrity: string;
  battery_present: boolean;
  version: string;
  offline: boolean;
}

export interface VerifyResponse {
  checks: Array<{ id: string; name: string; tier: string; state: string; detail: string; threshold: string; observed: string }>;
  aggregate: string;
  battery: Record<string, unknown> | null;
}

export interface Scenario {
  scenario_id: string;
  title: string;
  synthetic: boolean;
  state: {
    drugs: Array<{ drug_id: string; exposure_multiplier: number }>;
    k_o_mM: number;
    cl_ms: number;
    cell_type: string;
    solver_profile: string;
  };
}

const BASE = "/api/v1";

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.error_code ?? `HTTP ${r.status}`);
  }
  return r.json() as Promise<T>;
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json() as Promise<T>;
}

export const api = {
  health: () => get<HealthResponse>("/health"),
  drugs: () => get<{ drugs: unknown[] }>("/drugs"),
  scenarios: () => get<{ scenarios: unknown[] }>("/scenarios"),
  simulate: (req: SimulateRequest) => post<SimulateResponse>("/simulate", req),
  margin: (req: Record<string, unknown>) => post<MarginResponse>("/margin", req),
  rescue: (req: Record<string, unknown>) => post<RescueResponse>("/rescue", req),
  blindspot: (req: Record<string, unknown>) => post<Record<string, unknown>>("/blindspot", req),
  verify: (req: Record<string, unknown>) => post<VerifyResponse>("/verify", req),
};
