import type { DSBadgeColor } from "@/components/design-system";
import type { PlanCaseFilter, PlanCaseStatus } from "../types/plan-case-status.type";
import type { PlanStatusFilter } from "../types/plan-status-filter.type";
import type { PlanGapSeverity, PlanStatus } from "../types/plan.type";

export const MAX_PLAN_NAME_LENGTH = 120;

export const MAX_PLAN_DESCRIPTION_LENGTH = 2000;

export const MAX_PLAN_ITEMS = 100;

export const NOT_FOUND_STATUS = 404;

export const EMPTY_VALUE = "—";

export const PLAN_STATUS_FILTERS: PlanStatusFilter[] = ["all", "open", "signed_off", "closed"];

export const PLAN_STATUS_COLORS: Record<PlanStatus, DSBadgeColor> = {
  open: "tessio",
  signed_off: "green",
  closed: "gray",
};

export const PLAN_CASE_STATUSES: PlanCaseStatus[] = [
  "passed",
  "failed",
  "blocked",
  "skipped",
  "notRun",
];

export const PLAN_CASE_FILTERS: PlanCaseFilter[] = [
  "all",
  "failed",
  "blocked",
  "notRun",
  "skipped",
  "passed",
];

export const PLAN_CASE_STATUS_COLORS: Record<PlanCaseStatus, DSBadgeColor> = {
  passed: "green",
  failed: "red",
  blocked: "yellow",
  skipped: "gray",
  notRun: "gray",
};

export const PLAN_PROGRESS_STATUSES: PlanCaseStatus[] = ["passed", "failed", "blocked", "skipped"];

export const GAP_SEVERITY_COLORS: Record<PlanGapSeverity, DSBadgeColor> = {
  high: "red",
  medium: "orange",
  low: "gray",
};
