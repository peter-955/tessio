import type { DSChartDatum } from "@/components/design-system";
import { CATEGORY_KEY } from "../typing/constants/insights.constant";
import type { SprintCoverage } from "../typing/types/insights.type";

export const buildSprintCoverageData = (items: SprintCoverage[]): DSChartDatum[] => {
  return items.map((item) => {
    return {
      [CATEGORY_KEY]: item.sprint.name,
      passed: item.coverage.passedCount,
      failed: item.coverage.failedCount,
      blocked: item.coverage.blockedCount,
      notRun: item.coverage.notRunCount,
      uncovered: item.coverage.uncoveredCount,
    };
  });
};

export const checkSprintCoverageHasCriteria = (items: SprintCoverage[]): boolean => {
  return items.some((item) => {
    return item.coverage.criterionCount > 0;
  });
};
