import type { components } from "@/lib/api/openapi.type";

export type RunLog = components["schemas"]["RunLogResponse"];

export type RunLogEntry = components["schemas"]["RunLogEntryResponse"];

export type RunLogPhase = components["schemas"]["RunLogPhase"];

export interface RunLogLabel {
  key: string;
  values: Record<string, string>;
}

export interface RunLogSection {
  id: string;
  phase: RunLogPhase;
  testCaseId: string | null;
  entries: RunLogEntry[];
}
