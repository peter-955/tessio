import { RUN_STATUSES } from "@/shared/typing/constants/test-status.constant";
import type { RunStatus } from "@/shared/typing/types/test-run.type";
import {
  RUN_ID_PATTERN,
  RUN_LIST_LIMIT,
  STATUS_PARAMETER,
  STORY_KEY_PATTERN,
  STORY_PARAMETER,
  SUITE_PARAMETER,
} from "../typing/constants/run.constant";
import type { RunFilters, RunListQuery, RunSearchParams } from "../typing/types/run.type";

export const EMPTY_RUN_FILTERS: RunFilters = { status: null, storyKey: null, suiteId: null };

const readFirstValue = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue ?? null;
};

const isRunStatus = (value: string): value is RunStatus => {
  return (RUN_STATUSES as readonly string[]).includes(value);
};

export const readRunSearchParams = (searchParams: URLSearchParams): RunSearchParams => {
  const record: RunSearchParams = {};

  for (const key of new Set(searchParams.keys())) {
    const values = searchParams.getAll(key);
    record[key] = values.length === 1 ? values[0] : values;
  }

  return record;
};

export const parseRunFilters = (searchParams: RunSearchParams): RunFilters => {
  const status = readFirstValue(searchParams[STATUS_PARAMETER]);
  const storyKey = readFirstValue(searchParams[STORY_PARAMETER]);
  const suiteId = readFirstValue(searchParams[SUITE_PARAMETER]);

  return {
    status: status !== null && isRunStatus(status) ? status : null,
    storyKey: storyKey !== null && STORY_KEY_PATTERN.test(storyKey) ? storyKey.toUpperCase() : null,
    suiteId: suiteId !== null && RUN_ID_PATTERN.test(suiteId) ? suiteId.toLowerCase() : null,
  };
};

export const buildRunFiltersSearch = (filters: RunFilters): string => {
  const searchParams = new URLSearchParams();

  if (filters.status !== null) {
    searchParams.set(STATUS_PARAMETER, filters.status);
  }

  if (filters.storyKey !== null) {
    searchParams.set(STORY_PARAMETER, filters.storyKey);
  }

  if (filters.suiteId !== null) {
    searchParams.set(SUITE_PARAMETER, filters.suiteId);
  }

  const search = searchParams.toString();

  return search === "" ? "" : `?${search}`;
};

export const buildRunListQuery = (filters: RunFilters): RunListQuery => {
  return {
    ...(filters.storyKey === null ? {} : { storyKey: filters.storyKey }),
    ...(filters.suiteId === null ? {} : { suiteId: filters.suiteId }),
    ...(filters.status === null ? {} : { status: filters.status }),
    limit: RUN_LIST_LIMIT,
  };
};

export const checkHasRunFilters = (filters: RunFilters): boolean => {
  return filters.status !== null || filters.storyKey !== null || filters.suiteId !== null;
};
