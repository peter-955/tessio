import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { FailureStatusAction } from "../typing/types/failure-filters.type";
import type { FailureStatus } from "../typing/types/failure.type";

export const buildFailureStatusActions = (
  status: FailureStatus,
  project: Pick<Project, "capabilities" | "isArchived">,
): FailureStatusAction[] => {
  if (project.isArchived) {
    return [];
  }

  if (
    (status === "open" || status === "reopened") &&
    checkHasProjectCapability(project, "failure.mark_fixed")
  ) {
    return [{ status: "fixed", labelKey: "markFixed", type: "primary" }];
  }

  if (status === "fixed" && checkHasProjectCapability(project, "failure.verify")) {
    return [
      { status: "verified", labelKey: "verify", type: "primary" },
      { status: "reopened", labelKey: "reopen", type: "default" },
    ];
  }

  return [];
};
