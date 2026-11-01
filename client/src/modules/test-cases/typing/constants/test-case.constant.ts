import type { DSBadgeColor } from "@/components/design-system";
import type { StoryFilters } from "@/modules/stories/typing/types/story-filters.type";
import type { TestCasePriority, TestCaseStatus } from "../types/test-case.type";

export const TEST_CASE_STATUSES: TestCaseStatus[] = ["draft", "in_review", "ready", "deprecated"];

export const TEST_CASE_PRIORITIES: TestCasePriority[] = ["critical", "high", "medium", "low"];

export const TEST_CASE_STATUS_TRANSITIONS: Record<TestCaseStatus, readonly TestCaseStatus[]> = {
  draft: ["in_review", "deprecated"],
  in_review: ["draft", "ready", "deprecated"],
  ready: ["in_review", "draft", "deprecated"],
  deprecated: ["draft"],
};

export const TEST_CASE_PRIMARY_STATUS: Record<TestCaseStatus, TestCaseStatus | null> = {
  draft: "in_review",
  in_review: "ready",
  ready: null,
  deprecated: "draft",
};

export const TEST_CASE_STATUS_ACTION_ORDER: TestCaseStatus[] = [
  "ready",
  "in_review",
  "draft",
  "deprecated",
];

export const TEST_CASE_STATUS_COLORS: Record<TestCaseStatus, DSBadgeColor> = {
  draft: "gray",
  in_review: "yellow",
  ready: "green",
  deprecated: "gray",
};

export const TEST_CASE_PRIORITY_COLORS: Record<TestCasePriority, DSBadgeColor> = {
  critical: "red",
  high: "yellow",
  medium: "tessio",
  low: "gray",
};

export const DEFAULT_TEST_CASE_PRIORITY: TestCasePriority = "medium";

export const MAX_TITLE_LENGTH = 200;

export const MAX_TEXT_LENGTH = 5000;

export const MAX_STEPS = 100;

export const MAX_CRITERION_LINKS = 50;

export const QUERY_MAX_LENGTH = 100;

export const FILE_KEY_PATTERN = /^[A-Za-z][A-Za-z0-9_.-]{0,99}$/;

export const CASE_CODE_PATTERN = /^TC-[1-9][0-9]{0,8}$/i;

export const STORY_KEY_PATTERN = /^[A-Z][A-Z0-9_]*-[1-9][0-9]*$/i;

export const MAX_CASE_IMPORT_SIZE_IN_BYTES = 5242880;

export const XLSX_CONTENT_TYPE =
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

export const CSV_CONTENT_TYPE = "text/csv";

export const XLSX_FILE_EXTENSION = ".xlsx";

export const CSV_FILE_EXTENSION = ".csv";

export const SEARCH_DEBOUNCE_MILLISECONDS = 300;

export const NOT_FOUND_STATUS = 404;

export const TEST_CASE_DETAIL_TAB_PARAMETER = "tab";

export const STORY_PARAMETER = "story";

export const ALL_OPTION = "all";

export const ALL_STORIES_FILTERS: StoryFilters = { sprintId: null, testStatus: null, query: "" };

export const DATA_REFERENCE_PREFIX = "{{data.";

export const FILE_REFERENCE_PREFIX = "{{file.";
