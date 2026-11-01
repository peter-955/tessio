import { buildProjectPath } from "@/modules/projects/utils/project-path.util";
import { STORY_PARAMETER } from "../typing/constants/test-case.constant";

export const buildTestCasesPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "test-cases");
};

export const buildTestCasePath = (projectKey: string, caseCode: string): string => {
  return `${buildTestCasesPath(projectKey)}/${encodeURIComponent(caseCode)}`;
};

export const buildNewTestCasePath = (projectKey: string, storyKey: string | null): string => {
  const path = `${buildTestCasesPath(projectKey)}/new`;

  return storyKey === null
    ? path
    : `${path}?${new URLSearchParams({ [STORY_PARAMETER]: storyKey }).toString()}`;
};
