import { buildProjectPath } from "@/modules/projects/utils/project-path.util";

export const buildSprintsPath = (projectKey: string): string => {
  return buildProjectPath(projectKey, "sprints");
};

export const buildSprintPath = (projectKey: string, sprintId: string): string => {
  return `${buildSprintsPath(projectKey)}/${encodeURIComponent(sprintId)}`;
};
