import type { DSBadgeColor } from "../typing/types/badge.type";
import type {
  DSTraceabilityCriterionStatus,
  DSTraceabilityResultStatus,
} from "./traceability-matrix.type";

export const DS_TRACEABILITY_RESULT_COLORS: Record<DSTraceabilityResultStatus, DSBadgeColor> = {
  passed: "green",
  failed: "red",
  blocked: "yellow",
  skipped: "gray",
  not_run: "gray",
};

export const DS_TRACEABILITY_CRITERION_COLORS: Record<DSTraceabilityCriterionStatus, DSBadgeColor> =
  {
    passed: "green",
    failed: "red",
    blocked: "yellow",
    not_run: "gray",
    uncovered: "yellow",
  };
