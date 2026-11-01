import { buildProjectPath } from "@/modules/projects/utils/project-path.util";

export const buildRunPath = (projectKey: string, runId: string): string => {
  return `${buildProjectPath(projectKey, "runs")}/${encodeURIComponent(runId)}`;
};
