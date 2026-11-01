import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import {
  STORY_PARAMETER,
  TAB_PARAMETER,
  TEST_CASES_TAB,
} from "../typing/constants/manual-run.constant";

export const buildRunsPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "runs");
};

export const buildNewManualRunPath = (projectKey: string, storyKey?: string): string => {
  const path = `${buildRunsPath(projectKey)}/new`;

  return storyKey === undefined
    ? path
    : `${path}?${new URLSearchParams({ [STORY_PARAMETER]: storyKey }).toString()}`;
};

export const buildRunDetailPath = (projectKey: string, runId: string): string => {
  return `${buildRunsPath(projectKey)}/${encodeURIComponent(runId)}`;
};

export const buildRecordManualRunPath = (projectKey: string, runId: string): string => {
  return `${buildRunDetailPath(projectKey, runId)}/record`;
};

export const buildStoryTestCasesPath = (projectKey: string, storyKey: string): string => {
  const storyPath = buildProjectPath(projectKey, `stories/${encodeURIComponent(storyKey)}`);

  return `${storyPath}?${new URLSearchParams({ [TAB_PARAMETER]: TEST_CASES_TAB }).toString()}`;
};
