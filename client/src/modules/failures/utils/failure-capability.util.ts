import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { Failure } from "../typing/types/failure.type";

export const checkCanAssignFailure = (
  project: Pick<Project, "capabilities" | "isArchived">,
  failure: Pick<Failure, "status">,
): boolean => {
  return (
    !project.isArchived &&
    checkHasProjectCapability(project, "failure.assign") &&
    failure.status !== "verified"
  );
};
