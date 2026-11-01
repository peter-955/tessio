import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import type { FailureFilters } from "../typing/types/failure-filters.type";
import { buildFailureFiltersSearch } from "./failure-filters.util";

export const buildFailuresPath = (projectKey: string, filters?: FailureFilters): string => {
  const path = buildProjectPath(projectKey, "failures");

  return filters === undefined ? path : `${path}${buildFailureFiltersSearch(filters)}`;
};

export const buildFailurePath = (projectKey: string, failureId: string): string => {
  return `${buildFailuresPath(projectKey)}/${encodeURIComponent(failureId)}`;
};

export const buildFailureRunPath = (projectKey: string, runId: string): string => {
  return `${buildProjectPath(projectKey, "runs")}/${encodeURIComponent(runId)}`;
};
