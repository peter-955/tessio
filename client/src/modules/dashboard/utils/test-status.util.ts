import {
  TEST_STATUS_COUNT_FIELDS,
  TEST_STATUS_ORDER,
} from "../typing/constants/dashboard.constant";
import type { TestStatusCounts, TestStatusRow } from "../typing/types/dashboard.type";
import { buildSprintStoriesHref } from "./dashboard-path.util";

export const buildTestStatusRows = (
  projectKey: string,
  sprintId: string | null,
  counts: TestStatusCounts,
): TestStatusRow[] => {
  return TEST_STATUS_ORDER.map((status) => {
    return {
      status,
      count: counts[TEST_STATUS_COUNT_FIELDS[status]],
      href: buildSprintStoriesHref(projectKey, sprintId, status),
    };
  });
};
