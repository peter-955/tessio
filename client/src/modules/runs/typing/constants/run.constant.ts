import type { DSBadgeColor } from "@/components/design-system";
import type { CriterionStatus, RunCountKey } from "../types/run.type";

export const RUN_LIST_LIMIT = 50;

export const RUN_POLL_INTERVAL_IN_MILLISECONDS = 30000;

export const FILE_LINK_STALE_TIME_IN_MILLISECONDS = 240000;

export const STORY_OPTIONS_STALE_TIME_IN_MILLISECONDS = 300000;

export const RUN_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const STORY_KEY_PATTERN = /^[A-Z][A-Z0-9]*-[1-9][0-9]*$/i;

export const STATUS_PARAMETER = "status";

export const STORY_PARAMETER = "story";

export const TAB_PARAMETER = "tab";

export const ALL_OPTION = "all";

export const CRITERION_STATUS_COLORS: Record<CriterionStatus, DSBadgeColor> = {
  uncovered: "yellow",
  not_run: "gray",
  passed: "green",
  failed: "red",
  blocked: "yellow",
};

export const RUN_COUNT_KEYS: RunCountKey[] = [
  "passed",
  "failed",
  "blocked",
  "skipped",
  "notReported",
];

export const EXPANDED_CASE_STATUSES: readonly string[] = ["failed", "blocked"];

export const NOT_FOUND_STATUS = 404;

export const RUNS_TAB_PARAMETER_VALUE = "runs";

export const LOADING_ROW_COUNT = 5;
