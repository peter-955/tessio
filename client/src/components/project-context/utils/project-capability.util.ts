import type { Project, ProjectCapability } from "../typing/types/project.type";

export const checkHasProjectCapability = (
  project: Pick<Project, "capabilities">,
  capability: ProjectCapability,
): boolean => {
  return project.capabilities.includes(capability);
};
