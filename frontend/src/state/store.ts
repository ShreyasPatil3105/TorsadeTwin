import { create } from "zustand";
import { api, SimulateRequest, SimulateResponse, MarginResponse, RescueResponse, HealthResponse, VerifyResponse } from "../api/client";

interface Store {
  healthData: HealthResponse | null;
  simulate: SimulateResponse | null;
  margin: MarginResponse | null;
  rescue: RescueResponse | null;
  verify: VerifyResponse | null;
  request: SimulateRequest;
  loading: string | null;
  setRequest: (patch: Partial<SimulateRequest>) => void;
  fetchHealth: () => void;
  runSimulate: () => void;
  runMargin: () => void;
  runRescue: () => void;
  runVerify: () => void;
}

export const useStore = create<Store>((set, get) => ({
  healthData: null,
  simulate: null,
  margin: null,
  rescue: null,
  verify: null,
  request: { drugs: [], k_o_mM: 5.4, cl_ms: 2000, cell_type: "endo", solver_profile: "standard" },
  loading: null,
  setRequest: (patch) => set((s) => ({ request: { ...s.request, ...patch } })),
  fetchHealth: () => api.health().then((h) => set({ healthData: h })).catch(() => {}),
  runSimulate: () => {
    set({ loading: "simulate" });
    api.simulate(get().request).then((sim) => set({ simulate: sim, loading: null })).catch(() => set({ loading: null }));
  },
  runMargin: () => {
    set({ loading: "margin" });
    const req = get().request;
    const axes = ["k_o_mM", ...req.drugs.map((d) => `exposure:${d.drug_id}`)];
    api.margin({ ...req, axes, weights: {}, max_evals: 300 }).then((m) => set({ margin: m, loading: null })).catch(() => set({ loading: null }));
  },
  runRescue: () => {
    set({ loading: "rescue" });
    api.rescue({ ...get().request, tau: 0.05, cost_weights: { w_K: 1, w_E: 1, w_D: 6 }, allow_discontinuation: true, compute_post_margin: true })
      .then((r) => set({ rescue: r, loading: null })).catch(() => set({ loading: null }));
  },
  runVerify: () => {
    set({ loading: "verify" });
    api.verify({ scope: "request", state: get().request }).then((v) => set({ verify: v, loading: null })).catch(() => set({ loading: null }));
  },
}));
