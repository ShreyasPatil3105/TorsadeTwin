// Generated API types mirroring docs/openapi.snapshot.json (§21.4).
export * from "./client";

export type CredibilityState = "VERIFIED" | "UNVERIFIED" | "FAILED";

export interface DrugInfo {
  drug_id: string;
  drug_name: string;
  cmax_free_nM: number;
  discontinuable: boolean;
  dose_steps: number[];
  cipa_training_risk_label: string;
  qt_risk_class_manual: string | null;
  channels: Array<{ channel: string; ic50_nM: number | null; hill: number | null; source_doi: string; verification_status: string }>;
}
