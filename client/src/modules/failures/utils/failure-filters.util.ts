import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import {
  ACTIVE_FAILURE_STATUSES,
  ACTIVE_FILTER,
  ALL_FILTER,
  ASSIGNEE_PARAMETER,
  FAILURE_STATUSES,
  ME_FILTER,
  STATUS_PARAMETER,
  STORY_KEY_PATTERN,
  STORY_PARAMETER,
  UNASSIGNED_FILTER,
} from "../typing/constants/failure.constant";
import type {
  FailureAssigneeFilter,
  FailureFilters,
  FailureListQuery,
  FailureSearchParams,
  FailureStatusFilter,
} from "../typing/types/failure-filters.type";
import type { FailureStatus } from "../typing/types/failure.type";

export const EMPTY_FAILURE_FILTERS: FailureFilters = {
  status: ACTIVE_FILTER,
  assignee: null,
  storyKey: null,
};

const readFirstValue = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue ?? null;
};

const isFailureStatus = (value: string): value is FailureStatus => {
  return (FAILURE_STATUSES as readonly string[]).includes(value);
};

const parseStatusFilter = (value: string | null): FailureStatusFilter => {
  if (value === ALL_FILTER) {
    return ALL_FILTER;
  }

  return value !== null && isFailureStatus(value) ? value : ACTIVE_FILTER;
};

const parseAssigneeFilter = (value: string | null): FailureAssigneeFilter => {
  if (value === UNASSIGNED_FILTER || value === ME_FILTER) {
    return value;
  }

  return value !== null && UUID_PATTERN.test(value) ? value.toLowerCase() : null;
};

const buildStatusQuery = (status: FailureStatusFilter): FailureStatus[] | null => {
  if (status === ALL_FILTER) {
    return null;
  }

  return status === ACTIVE_FILTER ? [...ACTIVE_FAILURE_STATUSES] : [status];
};

const buildAssigneeQuery = (
  assignee: FailureAssigneeFilter,
  currentUserId: string,
): Pick<FailureListQuery, "assigneeId" | "unassigned"> => {
  if (assignee === null) {
    return {};
  }

  if (assignee === UNASSIGNED_FILTER) {
    return { unassigned: true };
  }

  return { assigneeId: assignee === ME_FILTER ? currentUserId : assignee };
};

export const readFailureSearchParams = (searchParams: URLSearchParams): FailureSearchParams => {
  const record: FailureSearchParams = {};

  for (const key of new Set(searchParams.keys())) {
    const values = searchParams.getAll(key);
    record[key] = values.length === 1 ? values[0] : values;
  }

  return record;
};

export const parseFailureFilters = (searchParams: FailureSearchParams): FailureFilters => {
  const storyKey = readFirstValue(searchParams[STORY_PARAMETER]);

  return {
    status: parseStatusFilter(readFirstValue(searchParams[STATUS_PARAMETER])),
    assignee: parseAssigneeFilter(readFirstValue(searchParams[ASSIGNEE_PARAMETER])),
    storyKey: storyKey !== null && STORY_KEY_PATTERN.test(storyKey) ? storyKey.toUpperCase() : null,
  };
};

export const buildFailureListQuery = (
  filters: FailureFilters,
  currentUserId: string,
): FailureListQuery => {
  const status = buildStatusQuery(filters.status);

  return {
    ...(status === null ? {} : { status }),
    ...buildAssigneeQuery(filters.assignee, currentUserId),
    ...(filters.storyKey === null ? {} : { storyKey: filters.storyKey }),
  };
};

export const buildFailureFiltersSearch = (filters: FailureFilters): string => {
  const searchParams = new URLSearchParams();

  if (filters.status !== ACTIVE_FILTER) {
    searchParams.set(STATUS_PARAMETER, filters.status);
  }

  if (filters.assignee !== null) {
    searchParams.set(ASSIGNEE_PARAMETER, filters.assignee);
  }

  if (filters.storyKey !== null) {
    searchParams.set(STORY_PARAMETER, filters.storyKey);
  }

  const search = searchParams.toString();

  return search === "" ? "" : `?${search}`;
};

export const checkHasFailureFilters = (filters: FailureFilters): boolean => {
  return (
    (filters.status !== ACTIVE_FILTER && filters.status !== ALL_FILTER) ||
    filters.assignee !== null ||
    filters.storyKey !== null
  );
};

export const clearFailureFilters = (): FailureFilters => {
  return EMPTY_FAILURE_FILTERS;
};
