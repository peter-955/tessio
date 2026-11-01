import { PROJECTS_PATH } from "../typing/constants/project-path.constant";

export const buildProjectPath = (projectKey: string, segment = ""): string => {
  const projectPath = `${PROJECTS_PATH}/${encodeURIComponent(projectKey)}`;

  return segment === "" ? projectPath : `${projectPath}/${segment}`;
};
