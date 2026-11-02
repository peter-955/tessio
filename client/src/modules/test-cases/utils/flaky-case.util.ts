import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { FLAKY_CASE_BADGES } from "../typing/constants/flaky-case.constant";
import type { FlakyCaseBadgeDefinition } from "../typing/types/flaky-case-badge.type";
import type { FlakyCaseFlags } from "../typing/types/flaky-case-flags.type";
import type { QuarantineTestCaseRequest } from "../typing/types/quarantine.type";

export const checkCanQuarantineTestCases = (
  project: Pick<Project, "capabilities" | "isArchived">,
): boolean => {
  return !project.isArchived && checkHasProjectCapability(project, "test_case.quarantine");
};

export const listFlakyCaseBadges = (flags: FlakyCaseFlags): FlakyCaseBadgeDefinition[] => {
  return FLAKY_CASE_BADGES.filter((definition) => flags[definition.flag]);
};

export const buildQuarantineRequest = (reason: string): QuarantineTestCaseRequest => {
  const trimmedReason = reason.trim();

  return trimmedReason === "" ? {} : { reason: trimmedReason };
};
