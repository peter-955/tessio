import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import type { RunDetailTab } from "../typing/enums/run-detail-tab.enum";
import type { RunFilters } from "../typing/types/run.type";
import { buildRunFiltersSearch, EMPTY_RUN_FILTERS } from "./run-filters.util";

export const buildRunsPath = (projectKey: string, filters: Partial<RunFilters> = {}): string => {
  return `${buildProjectPath(projectKey, "runs")}${buildRunFiltersSearch({ ...EMPTY_RUN_FILTERS, ...filters })}`;
};

export const buildRunPath = (projectKey: string, runId: string, tab?: RunDetailTab): string => {
  const path = `${buildProjectPath(projectKey, "runs")}/${encodeURIComponent(runId)}`;

  return tab === undefined ? path : `${path}?${new URLSearchParams({ tab }).toString()}`;
};

export const buildCasePath = (projectKey: string, code: string): string => {
  return buildProjectPath(projectKey, `test-cases/${encodeURIComponent(code)}`);
};

export const buildCaseVersionPath = (
  projectKey: string,
  code: string,
  versionNumber: number,
): string => {
  return `${buildCasePath(projectKey, code)}?tab=history&version=${versionNumber}`;
};

export const buildStoryPath = (projectKey: string, jiraKey: string, tab?: string): string => {
  const path = buildProjectPath(projectKey, `stories/${encodeURIComponent(jiraKey)}`);

  return tab === undefined ? path : `${path}?${new URLSearchParams({ tab }).toString()}`;
};
