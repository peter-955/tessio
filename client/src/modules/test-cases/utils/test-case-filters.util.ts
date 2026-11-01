import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import {
  QUERY_MAX_LENGTH,
  STORY_KEY_PATTERN,
  STORY_PARAMETER,
  TEST_CASE_PRIORITIES,
  TEST_CASE_STATUSES,
} from "../typing/constants/test-case.constant";
import type {
  TestCaseFilters,
  TestCaseListQuery,
  TestCaseSearchParams,
} from "../typing/types/test-case-filters.type";
import type { TestCasePriority, TestCaseStatus } from "../typing/types/test-case.type";

const STATUS_PARAMETER = "status";
const PRIORITY_PARAMETER = "priority";
const CRITERION_PARAMETER = "criterion";
const NEEDS_REVIEW_PARAMETER = "needsReview";
const QUERY_PARAMETER = "query";
const TRUE_VALUE = "true";

export const EMPTY_TEST_CASE_FILTERS: TestCaseFilters = {
  storyKey: null,
  status: null,
  priority: null,
  criterionId: null,
  isNeedingReview: false,
  query: "",
};

const readFirstValue = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue ?? null;
};

const isTestCaseStatus = (value: string): value is TestCaseStatus => {
  return (TEST_CASE_STATUSES as readonly string[]).includes(value);
};

const isTestCasePriority = (value: string): value is TestCasePriority => {
  return (TEST_CASE_PRIORITIES as readonly string[]).includes(value);
};

export const readTestCaseSearchParams = (searchParams: URLSearchParams): TestCaseSearchParams => {
  const record: TestCaseSearchParams = {};

  for (const key of new Set(searchParams.keys())) {
    const values = searchParams.getAll(key);
    record[key] = values.length === 1 ? values[0] : values;
  }

  return record;
};

export const parseTestCaseFilters = (searchParams: TestCaseSearchParams): TestCaseFilters => {
  const storyKey = readFirstValue(searchParams[STORY_PARAMETER]);
  const status = readFirstValue(searchParams[STATUS_PARAMETER]);
  const priority = readFirstValue(searchParams[PRIORITY_PARAMETER]);
  const criterionId = readFirstValue(searchParams[CRITERION_PARAMETER]);
  const query = readFirstValue(searchParams[QUERY_PARAMETER]);
  const validStoryKey =
    storyKey !== null && STORY_KEY_PATTERN.test(storyKey) ? storyKey.toUpperCase() : null;

  return {
    storyKey: validStoryKey,
    status: status !== null && isTestCaseStatus(status) ? status : null,
    priority: priority !== null && isTestCasePriority(priority) ? priority : null,
    criterionId:
      validStoryKey !== null && criterionId !== null && UUID_PATTERN.test(criterionId)
        ? criterionId
        : null,
    isNeedingReview: readFirstValue(searchParams[NEEDS_REVIEW_PARAMETER]) === TRUE_VALUE,
    query: (query ?? "").slice(0, QUERY_MAX_LENGTH),
  };
};

export const buildTestCaseListQuery = (filters: TestCaseFilters): TestCaseListQuery => {
  const trimmedQuery = filters.query.trim();

  return {
    ...(filters.storyKey === null ? {} : { storyKey: filters.storyKey }),
    ...(filters.status === null ? {} : { status: filters.status }),
    ...(filters.priority === null ? {} : { priority: filters.priority }),
    ...(filters.criterionId === null ? {} : { criterionId: filters.criterionId }),
    ...(filters.isNeedingReview ? { needsReview: true } : {}),
    ...(trimmedQuery === "" ? {} : { query: trimmedQuery }),
  };
};

export const buildTestCaseFiltersSearch = (filters: TestCaseFilters): string => {
  const searchParams = new URLSearchParams();
  const trimmedQuery = filters.query.trim();

  if (filters.storyKey !== null) {
    searchParams.set(STORY_PARAMETER, filters.storyKey);
  }

  if (filters.status !== null) {
    searchParams.set(STATUS_PARAMETER, filters.status);
  }

  if (filters.priority !== null) {
    searchParams.set(PRIORITY_PARAMETER, filters.priority);
  }

  if (filters.storyKey !== null && filters.criterionId !== null) {
    searchParams.set(CRITERION_PARAMETER, filters.criterionId);
  }

  if (filters.isNeedingReview) {
    searchParams.set(NEEDS_REVIEW_PARAMETER, TRUE_VALUE);
  }

  if (trimmedQuery !== "") {
    searchParams.set(QUERY_PARAMETER, trimmedQuery);
  }

  const search = searchParams.toString();

  return search === "" ? "" : `?${search}`;
};

export const checkHasTestCaseFilters = (
  filters: TestCaseFilters,
  isStoryFixed: boolean,
): boolean => {
  return (
    filters.status !== null ||
    filters.priority !== null ||
    filters.criterionId !== null ||
    filters.isNeedingReview ||
    filters.query.trim() !== "" ||
    (!isStoryFixed && filters.storyKey !== null)
  );
};

export const clearTestCaseFilters = (
  filters: TestCaseFilters,
  isStoryFixed: boolean,
): TestCaseFilters => {
  return { ...EMPTY_TEST_CASE_FILTERS, storyKey: isStoryFixed ? filters.storyKey : null };
};
