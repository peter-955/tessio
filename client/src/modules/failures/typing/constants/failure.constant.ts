import type { DSBadgeColor } from "@/components/design-system";
import type { FailureStatus, ResultStatus } from "../types/failure.type";

export const FAILURE_STATUSES: FailureStatus[] = ["open", "reopened", "fixed", "verified"];

export const ACTIVE_FAILURE_STATUSES: FailureStatus[] = ["open", "fixed", "reopened"];

export const FAILURE_STATUS_COLORS: Record<FailureStatus, DSBadgeColor> = {
  open: "red",
  reopened: "red",
  fixed: "yellow",
  verified: "green",
};

export const RESULT_STATUS_COLORS: Record<ResultStatus, DSBadgeColor> = {
  passed: "green",
  failed: "red",
  blocked: "yellow",
  skipped: "gray",
};

export const STATUS_PARAMETER = "status";

export const ASSIGNEE_PARAMETER = "assignee";

export const STORY_PARAMETER = "story";

export const ACTIVE_FILTER = "active";

export const ALL_FILTER = "all";

export const UNASSIGNED_FILTER = "unassigned";

export const ME_FILTER = "me";

export const ANY_ASSIGNEE_OPTION = "__any__";

export const UNASSIGNED_OPTION = "__unassigned__";

export const STORY_KEY_PATTERN = /^[A-Z][A-Z0-9_]*-[1-9][0-9]*$/i;

export const NOT_FOUND_STATUS = 404;

export const SCREENSHOT_LINK_STALE_MILLISECONDS = 240000;

export const SCREENSHOT_POLL_MILLISECONDS = 5000;

export const ASSIGN_FAILURE_FORM_ID = "assign-failure-form";

export const EMPTY_VALUE = "—";
