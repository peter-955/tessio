import type { Environment } from "./environment.type";

export interface DataGridColumn {
  scopeId: string;
  environment: Environment | null;
  isArchived: boolean;
}
