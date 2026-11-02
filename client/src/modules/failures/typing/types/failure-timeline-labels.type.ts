import type { SuspectedCause } from "@/shared/typing/types/test-run.type";
import type { FailureStatus } from "./failure.type";

export interface FailureTimelineLabels {
  opened: string;
  failedAgain: string;
  unassigned: string;
  automatic: string;
  formatStatusChange: (fromStatus: FailureStatus | null, toStatus: FailureStatus | null) => string;
  formatAssigned: (assigneeName: string) => string;
  formatCauseChange: (fromCause: SuspectedCause | null, toCause: SuspectedCause | null) => string;
  formatActor: (actorName: string) => string;
  formatTime: (isoDate: string) => string;
}
