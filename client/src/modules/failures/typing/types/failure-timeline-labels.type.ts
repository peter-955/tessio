import type { FailureStatus } from "./failure.type";

export interface FailureTimelineLabels {
  opened: string;
  failedAgain: string;
  unassigned: string;
  automatic: string;
  formatStatusChange: (fromStatus: FailureStatus | null, toStatus: FailureStatus | null) => string;
  formatAssigned: (assigneeName: string) => string;
  formatActor: (actorName: string) => string;
  formatTime: (isoDate: string) => string;
}
