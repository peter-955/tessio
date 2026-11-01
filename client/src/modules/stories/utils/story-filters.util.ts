import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import { STORY_QUERY_MAX_LENGTH, TEST_STATUSES } from "../typing/constants/story.constant";
import type {
  StoryFilters,
  StoryListQuery,
  StorySearchParams,
} from "../typing/types/story-filters.type";
import type { TestStatus } from "../typing/types/story.type";

const SPRINT_PARAMETER = "sprint";
const STATUS_PARAMETER = "status";
const QUERY_PARAMETER = "query";

const readFirstValue = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue ?? null;
};

const isTestStatus = (value: string): value is TestStatus => {
  return (TEST_STATUSES as readonly string[]).includes(value);
};

export const readStorySearchParams = (searchParams: URLSearchParams): StorySearchParams => {
  const record: StorySearchParams = {};

  for (const key of new Set(searchParams.keys())) {
    const values = searchParams.getAll(key);
    record[key] = values.length === 1 ? values[0] : values;
  }

  return record;
};

export const parseStoryFilters = (searchParams: StorySearchParams): StoryFilters => {
  const sprintId = readFirstValue(searchParams[SPRINT_PARAMETER]);
  const testStatus = readFirstValue(searchParams[STATUS_PARAMETER]);
  const query = readFirstValue(searchParams[QUERY_PARAMETER]);

  return {
    sprintId: sprintId !== null && UUID_PATTERN.test(sprintId) ? sprintId : null,
    testStatus: testStatus !== null && isTestStatus(testStatus) ? testStatus : null,
    query: (query ?? "").slice(0, STORY_QUERY_MAX_LENGTH),
  };
};

export const buildStoryListQuery = (filters: StoryFilters): StoryListQuery => {
  const trimmedQuery = filters.query.trim();

  return {
    ...(filters.sprintId === null ? {} : { sprintId: filters.sprintId }),
    ...(filters.testStatus === null ? {} : { testStatus: filters.testStatus }),
    ...(trimmedQuery === "" ? {} : { query: trimmedQuery }),
  };
};

export const buildStoryFiltersSearch = (filters: StoryFilters): string => {
  const searchParams = new URLSearchParams();
  const trimmedQuery = filters.query.trim();

  if (filters.sprintId !== null) {
    searchParams.set(SPRINT_PARAMETER, filters.sprintId);
  }

  if (filters.testStatus !== null) {
    searchParams.set(STATUS_PARAMETER, filters.testStatus);
  }

  if (trimmedQuery !== "") {
    searchParams.set(QUERY_PARAMETER, trimmedQuery);
  }

  const search = searchParams.toString();

  return search === "" ? "" : `?${search}`;
};

export const checkHasStoryFilters = (filters: StoryFilters, isSprintFixed: boolean): boolean => {
  return (
    filters.testStatus !== null ||
    filters.query.trim() !== "" ||
    (!isSprintFixed && filters.sprintId !== null)
  );
};
