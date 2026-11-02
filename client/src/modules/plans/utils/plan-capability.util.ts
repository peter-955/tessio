import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { PlanDetail } from "../typing/types/plan.type";

type ProjectAccess = Pick<Project, "capabilities" | "isArchived">;

export const checkCanCreatePlan = (project: ProjectAccess): boolean => {
  return !project.isArchived && checkHasProjectCapability(project, "plan.edit");
};

export const checkCanEditPlan = (
  project: ProjectAccess,
  plan: Pick<PlanDetail, "status">,
): boolean => {
  return checkCanCreatePlan(project) && plan.status === "open";
};

export const checkCanSignOffPlan = (
  project: ProjectAccess,
  plan: Pick<PlanDetail, "status">,
): boolean => {
  return (
    !project.isArchived &&
    checkHasProjectCapability(project, "plan.sign_off") &&
    plan.status === "open"
  );
};

export const checkCanClosePlan = (
  project: ProjectAccess,
  plan: Pick<PlanDetail, "status">,
): boolean => {
  return checkCanCreatePlan(project) && plan.status !== "closed";
};
