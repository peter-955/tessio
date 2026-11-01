import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import {
  ASSIGNEE_PARAMETER,
  SPRINT_PARAMETER,
  STATUS_PARAMETER,
  STORY_PARAMETER,
  UNASSIGNED_FAILURE_FILTER,
} from "../typing/constants/dashboard.constant";
import type { TestStatus } from "../typing/types/dashboard.type";

const buildQuery = (parameters: Record<string, string>): string => {
  const search = new URLSearchParams(parameters).toString();

  return search === "" ? "" : `?${search}`;
};

export const buildSprintStoriesHref = (
  projectKey: string,
  sprintId: string | null,
  status: TestStatus | null,
): string => {
  return `${buildProjectPath(projectKey, "stories")}${buildQuery({
    ...(sprintId === null ? {} : { [SPRINT_PARAMETER]: sprintId }),
    ...(status === null ? {} : { [STATUS_PARAMETER]: status }),
  })}`;
};

export const buildStoryHref = (projectKey: string, jiraKey: string): string => {
  return buildProjectPath(projectKey, `stories/${encodeURIComponent(jiraKey)}`);
};

export const buildNewCaseHref = (projectKey: string, jiraKey: string): string => {
  return `${buildProjectPath(projectKey, "test-cases/new")}${buildQuery({ [STORY_PARAMETER]: jiraKey })}`;
};

export const buildCaseHref = (projectKey: string, code: string): string => {
  return buildProjectPath(projectKey, `test-cases/${encodeURIComponent(code)}`);
};

export const buildFailuresHref = (projectKey: string): string => {
  return buildProjectPath(projectKey, "failures");
};

export const buildFailureHref = (projectKey: string, failureId: string): string => {
  return `${buildFailuresHref(projectKey)}/${encodeURIComponent(failureId)}`;
};

export const buildUnassignedFailuresHref = (projectKey: string): string => {
  return `${buildFailuresHref(projectKey)}${buildQuery({ [ASSIGNEE_PARAMETER]: UNASSIGNED_FAILURE_FILTER })}`;
};

export const buildRunsHref = (projectKey: string): string => {
  return buildProjectPath(projectKey, "runs");
};

export const buildRunHref = (projectKey: string, runId: string): string => {
  return `${buildRunsHref(projectKey)}/${encodeURIComponent(runId)}`;
};
