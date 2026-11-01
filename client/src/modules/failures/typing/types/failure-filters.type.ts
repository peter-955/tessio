import type {
  ACTIVE_FILTER,
  ALL_FILTER,
  ME_FILTER,
  UNASSIGNED_FILTER,
} from "../constants/failure.constant";
import type { FailureStatus } from "./failure.type";

export type FailureStatusFilter = FailureStatus | typeof ACTIVE_FILTER | typeof ALL_FILTER;

export type FailureAssigneeFilter = typeof UNASSIGNED_FILTER | typeof ME_FILTER | string | null;

export interface FailureFilters {
  status: FailureStatusFilter;
  assignee: FailureAssigneeFilter;
  storyKey: string | null;
}

export interface FailureListQuery {
  status?: FailureStatus[];
  assigneeId?: string;
  unassigned?: boolean;
  storyKey?: string;
}

export type FailureSearchParams = Record<string, string | string[] | undefined>;

export interface FailureStatusAction {
  status: FailureStatus;
  labelKey: "markFixed" | "verify" | "reopen";
  type: "primary" | "default";
}
