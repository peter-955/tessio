import type { DSBadgeColor } from "@/components/design-system";
import type { ResultStatus } from "../types/manual-run.type";

export const RESULT_STATUS_ORDER: readonly ResultStatus[] = [
  "passed",
  "failed",
  "blocked",
  "skipped",
];

export const RESULT_STATUS_COLORS: Record<ResultStatus, DSBadgeColor> = {
  passed: "green",
  failed: "red",
  blocked: "yellow",
  skipped: "gray",
};

export const SUGGESTION_PRIORITY: readonly ResultStatus[] = ["failed", "blocked", "passed"];

export const FALLBACK_RESULT_STATUS: ResultStatus = "skipped";

export const ERROR_RESULT_STATUSES: readonly ResultStatus[] = ["failed", "blocked"];

export const NOT_REPORTED_CHOICE = "not_reported";

export const USE_SUGGESTED_CHOICE = "suggested";
