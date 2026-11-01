import type { DSBadgeColor } from "@/components/design-system";
import type { ProjectRole } from "@/components/project-context/typing/types/project.type";
import type {
  AssignableRole,
  GapDataScope,
  GapSeverity,
  GapStatus,
  GapStatusFilter,
  GapTargetType,
  GapType,
  InboxFilter,
} from "../types/gap.type";
import type { RaiseGapValues } from "../types/raise-gap-values.type";

export const MAX_QUESTION_LENGTH = 2000;

export const MAX_ANSWER_LENGTH = 4000;

export const MAX_INBOX_SIZE = 200;

export const MAX_TARGET_LABEL_LENGTH = 80;

export const TARGET_LABEL_ELLIPSIS = "…";

export const GAP_TYPES: readonly GapType[] = [
  "missing_ac",
  "unclear_goal",
  "missing_step",
  "missing_test_data",
  "other",
];

export const GAP_SEVERITIES: readonly GapSeverity[] = ["high", "medium", "low"];

export const GAP_TARGET_TYPES: readonly GapTargetType[] = ["story", "criterion", "test_case"];

export const GAP_DATA_SCOPES: readonly GapDataScope[] = ["project", "environment"];

export const GAP_STATUS_FILTERS: readonly GapStatusFilter[] = ["open", "resolved", "all"];

export const INBOX_FILTERS: readonly InboxFilter[] = ["open", "all"];

export const INBOX_FILTER_LABEL_KEYS = {
  open: "inbox.filterOpen",
  all: "inbox.filterAll",
} as const satisfies Record<InboxFilter, string>;

export const GAP_SEVERITY_COLORS: Record<GapSeverity, DSBadgeColor> = {
  high: "red",
  medium: "yellow",
  low: "gray",
};

export const GAP_STATUS_COLORS: Record<GapStatus, DSBadgeColor> = {
  open: "yellow",
  resolved: "green",
};

export const ASSIGNABLE_ROLES: readonly AssignableRole[] = ["admin", "pm", "ba", "qc", "dev"];

export const REOPENING_ROLES: readonly ProjectRole[] = ["qc", "admin"];

export const GAPS_TAB_PARAMETER_VALUE = "gaps";

export const MISSING_TEST_DATA_TYPE: GapType = "missing_test_data";

export const MEMBER_CHOICE_PREFIX = "member:";

export const ROLE_CHOICE_PREFIX = "role:";

export const GAP_SKELETON_INDEXES: readonly number[] = [0, 1, 2];

export const RAISE_GAP_FORM_ID = "raise-gap-form";

export const ANSWER_GAP_FORM_ID = "answer-gap-form";

export const REASSIGN_GAP_FORM_ID = "reassign-gap-form";

export const RAISE_GAP_INITIAL_VALUES: RaiseGapValues = {
  type: null,
  severity: "medium",
  targetType: "story",
  targetRef: null,
  dataScope: null,
  question: "",
  assigneeId: null,
};
