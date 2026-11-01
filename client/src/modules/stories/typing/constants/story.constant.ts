import type { DSBadgeColor, DSIconName } from "@/components/design-system";
import { StoryDetailTab } from "../enums/story-detail-tab.enum";
import type { StorySlotTab } from "../types/story-detail-slots.type";
import type { StoryProgressColumn } from "../types/story-progress-column.type";
import type { TestStatus } from "../types/story.type";
import type {
  ActionableTestStatus,
  SignOffTestStatus,
  TestStatusAction,
} from "../types/test-status-action.type";

export const TEST_STATUSES: TestStatus[] = [
  "not_started",
  "ready_for_test",
  "in_test",
  "passed",
  "failed",
];

export const TEST_STATUS_COLORS: Record<TestStatus, DSBadgeColor> = {
  not_started: "gray",
  ready_for_test: "yellow",
  in_test: "tessio",
  passed: "green",
  failed: "red",
};

export const TEST_STATUS_ACTION_ORDER: ActionableTestStatus[] = [
  "ready_for_test",
  "passed",
  "failed",
  "not_started",
];

export const TEST_STATUS_ACTIONS: Record<ActionableTestStatus, TestStatusAction> = {
  ready_for_test: { label: "markReadyForTest", buttonType: "primary" },
  passed: { label: "markPassed", buttonType: "primary" },
  failed: { label: "markFailed", buttonType: "danger" },
  not_started: { label: "markNotStarted", buttonType: "outline" },
};

export const SIGN_OFF_STATUSES: SignOffTestStatus[] = ["passed", "failed"];

export const STORY_QUERY_MAX_LENGTH = 100;

export const SEARCH_DEBOUNCE_MILLISECONDS = 300;

export const NOT_FOUND_STATUS = 404;

export const STORY_DETAIL_TAB_PARAMETER = "tab";

export const STORY_SLOT_TAB_ORDER: StorySlotTab[] = [
  StoryDetailTab.TEST_CASES,
  StoryDetailTab.GAPS,
  StoryDetailTab.RUNS,
  StoryDetailTab.TRACEABILITY,
];

export const STORY_SLOT_TAB_ICONS: Record<StorySlotTab, DSIconName> = {
  [StoryDetailTab.TEST_CASES]: "testCases",
  [StoryDetailTab.GAPS]: "alertCircle",
  [StoryDetailTab.RUNS]: "runs",
  [StoryDetailTab.TRACEABILITY]: "circleCheck",
};

export const STORY_SLOT_TAB_LABELS: Record<
  StorySlotTab,
  "testCases" | "gaps" | "runs" | "traceability"
> = {
  [StoryDetailTab.TEST_CASES]: "testCases",
  [StoryDetailTab.GAPS]: "gaps",
  [StoryDetailTab.RUNS]: "runs",
  [StoryDetailTab.TRACEABILITY]: "traceability",
};

export const STORY_PROGRESS_COLUMNS: StoryProgressColumn[] = [
  { label: "coverage", isNumeric: true },
  { label: "openGaps", isNumeric: true },
  { label: "failures", isNumeric: true },
  { label: "lastRun", isNumeric: false },
];
