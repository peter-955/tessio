import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";

export const checkCanEditSharedSteps = (
  project: Pick<Project, "capabilities" | "isArchived">,
): boolean => {
  return !project.isArchived && checkHasProjectCapability(project, "test_case.edit");
};
