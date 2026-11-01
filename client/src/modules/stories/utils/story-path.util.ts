import { buildProjectPath } from "@/modules/projects/utils/project-path.util";

export const buildStoriesPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "stories");
};

export const buildStoryPath = (projectKey: string, jiraKey: string): string => {
  return `${buildStoriesPath(projectKey)}/${encodeURIComponent(jiraKey)}`;
};
