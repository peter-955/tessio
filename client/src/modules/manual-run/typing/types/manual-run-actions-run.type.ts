import type { RunExecutor, RunStatus } from "./manual-run.type";

export interface ManualRunActionsRun {
  id: string;
  executor: RunExecutor;
  status: RunStatus;
  startedBy: string;
  failedCount: number;
  blockedCount: number;
}
