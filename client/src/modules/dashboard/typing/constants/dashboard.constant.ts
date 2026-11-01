import type { DSBadgeColor } from "@/components/design-system";
import { CoverageSegmentKind } from "../enums/coverage-segment-kind.enum";
import type {
  CoverageCounts,
  SprintState,
  TestStatus,
  TestStatusCounts,
} from "../types/dashboard.type";
import type { FailureStatus, GapSeverity, TestCaseStatus } from "../types/my-work.type";
import type { RunStatus } from "../types/recent-run.type";

export const RECENT_RUNS_LIMIT = 5;

export const SPRINT_PARAMETER = "sprint";

export const STATUS_PARAMETER = "status";

export const STORY_PARAMETER = "story";

export const ASSIGNEE_PARAMETER = "assignee";

export const TEST_STATUS_ORDER: TestStatus[] = [
  "not_started",
  "ready_for_test",
  "in_test",
  "passed",
  "failed",
];

export const TEST_STATUS_COUNT_FIELDS: Record<TestStatus, keyof TestStatusCounts> = {
  not_started: "notStarted",
  ready_for_test: "readyForTest",
  in_test: "inTest",
  passed: "passed",
  failed: "failed",
};

export const TEST_STATUS_COLORS: Record<TestStatus, DSBadgeColor> = {
  not_started: "gray",
  ready_for_test: "yellow",
  in_test: "tessio",
  passed: "green",
  failed: "red",
};

export const RUN_STATUS_COLORS: Record<RunStatus, DSBadgeColor> = {
  running: "tessio",
  passed: "green",
  failed: "red",
  aborted: "gray",
};

export const SPRINT_STATE_COLORS: Record<SprintState, DSBadgeColor> = {
  active: "green",
  future: "tessio",
  closed: "gray",
};

export const GAP_SEVERITY_COLORS: Record<GapSeverity, DSBadgeColor> = {
  high: "red",
  medium: "yellow",
  low: "gray",
};

export const CASE_STATUS_COLORS: Record<TestCaseStatus, DSBadgeColor> = {
  draft: "gray",
  in_review: "yellow",
  ready: "green",
  deprecated: "gray",
};

export const FAILURE_STATUS_COLORS: Record<FailureStatus, DSBadgeColor> = {
  open: "red",
  reopened: "red",
  fixed: "yellow",
  verified: "green",
};

export const COVERAGE_SEGMENT_ORDER: CoverageSegmentKind[] = [
  CoverageSegmentKind.PASSED,
  CoverageSegmentKind.FAILED,
  CoverageSegmentKind.BLOCKED,
  CoverageSegmentKind.NOT_RUN,
  CoverageSegmentKind.UNCOVERED,
];

export const NOT_FOUND_STATUS = 404;

export const UNASSIGNED_FAILURE_FILTER = "unassigned";

export const GAP_INBOX_PATH = "/gaps";

export const MISSING_SPRINT_DATE = "?";

export const COVERAGE_SEGMENT_COUNT_FIELDS: Record<CoverageSegmentKind, keyof CoverageCounts> = {
  [CoverageSegmentKind.PASSED]: "passedCount",
  [CoverageSegmentKind.FAILED]: "failedCount",
  [CoverageSegmentKind.BLOCKED]: "blockedCount",
  [CoverageSegmentKind.NOT_RUN]: "notRunCount",
  [CoverageSegmentKind.UNCOVERED]: "uncoveredCount",
};
