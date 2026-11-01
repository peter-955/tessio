import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { TestCaseStatus } from "../typing/types/test-case.type";

export const checkCanEditTestCases = (
  project: Pick<Project, "capabilities" | "isArchived">,
): boolean => {
  return !project.isArchived && checkHasProjectCapability(project, "test_case.edit");
};

export const checkIsTestCaseReadOnly = (
  project: Pick<Project, "capabilities" | "isArchived">,
  status: TestCaseStatus,
): boolean => {
  return !checkCanEditTestCases(project) || status === "deprecated";
};
