import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import { SUITE_PARAMETER } from "../typing/constants/suite.constant";

export const buildSuitesPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "suites");
};

export const buildSuitePath = (projectKey: string, suiteId: string): string => {
  return `${buildSuitesPath(projectKey)}/${encodeURIComponent(suiteId)}`;
};

export const buildSuiteRunsPath = (projectKey: string, suiteId: string): string => {
  return `${buildProjectPath(projectKey, "runs")}?${new URLSearchParams({ [SUITE_PARAMETER]: suiteId }).toString()}`;
};

export const buildNewSuiteRunPath = (projectKey: string, suiteId: string): string => {
  return `${buildProjectPath(projectKey, "runs/new")}?${new URLSearchParams({ [SUITE_PARAMETER]: suiteId }).toString()}`;
};
