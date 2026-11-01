import type { DSBadgeColor } from "@/components/design-system";
import type { CoverageHighlightKind } from "../types/coverage-highlight.type";
import type { ResultStatus, RunStatus } from "../types/traceability.type";

export const RUN_STATUS_COLORS: Record<RunStatus, DSBadgeColor> = {
  running: "tessio",
  passed: "green",
  failed: "red",
  aborted: "gray",
};

export const COVERAGE_HIGHLIGHT_COLORS: Record<CoverageHighlightKind, DSBadgeColor> = {
  failing: "red",
  blocked: "yellow",
  uncovered: "yellow",
  allPassing: "green",
};

export const RESULT_STATUS_COLORS: Record<ResultStatus | "not_run", DSBadgeColor> = {
  passed: "green",
  failed: "red",
  blocked: "yellow",
  skipped: "gray",
  not_run: "gray",
};
