import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import { SPRINT_PARAMETER } from "../typing/constants/dashboard.constant";
import type { DashboardSearchParams } from "../typing/types/dashboard-search.type";

const readFirstValue = (value: string | string[] | undefined): string | null => {
  const firstValue = Array.isArray(value) ? value[0] : value;

  return firstValue ?? null;
};

export const parseDashboardSprintId = (searchParams: DashboardSearchParams): string | null => {
  const sprintId = readFirstValue(searchParams[SPRINT_PARAMETER]);

  return sprintId !== null && UUID_PATTERN.test(sprintId) ? sprintId : null;
};

export const readDashboardSearchParams = (searchParams: URLSearchParams): DashboardSearchParams => {
  const record: DashboardSearchParams = {};

  for (const key of new Set(searchParams.keys())) {
    const values = searchParams.getAll(key);
    record[key] = values.length === 1 ? values[0] : values;
  }

  return record;
};

export const buildDashboardSearch = (sprintId: string | null): string => {
  if (sprintId === null) {
    return "";
  }

  return `?${new URLSearchParams({ [SPRINT_PARAMETER]: sprintId }).toString()}`;
};
