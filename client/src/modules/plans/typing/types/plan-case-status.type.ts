import type { PlanResultStatus } from "./plan.type";

export type PlanCaseStatus = PlanResultStatus | "notRun";

export type PlanCaseFilter = PlanCaseStatus | "all";
