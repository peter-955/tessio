import type { PlanCaseStatus } from "./plan-case-status.type";

export interface PlanProgressSegment {
  status: PlanCaseStatus;
  count: number;
  percent: number;
}
