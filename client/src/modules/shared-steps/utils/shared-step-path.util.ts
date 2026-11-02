import { buildProjectPath } from "@/modules/projects/utils/project-path.util";

export const buildSharedStepsPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "shared-steps");
};

export const buildSharedStepPath = (projectKey: string, sharedStepKey: string): string => {
  return `${buildSharedStepsPath(projectKey)}/${encodeURIComponent(sharedStepKey)}`;
};
