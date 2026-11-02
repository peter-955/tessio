import { PLAN_PROGRESS_STATUSES } from "../typing/constants/plan.constant";
import type { PlanCaseFilter, PlanCaseStatus } from "../typing/types/plan-case-status.type";
import type { PlanProgressSegment } from "../typing/types/plan-progress-segment.type";
import type { PlanProgressWindow } from "../typing/types/plan-progress-window.type";
import type { PlanCase, PlanDetail, PlanProgressCounts } from "../typing/types/plan.type";

const FULL_PERCENT = 100;

export const readStatusCount = (counts: PlanProgressCounts, status: PlanCaseStatus): number => {
  return counts[status];
};

const toPercent = (count: number, total: number): number => {
  return total === 0 ? 0 : (count / total) * FULL_PERCENT;
};

export const buildProgressSegments = (counts: PlanProgressCounts): PlanProgressSegment[] => {
  return PLAN_PROGRESS_STATUSES.map((status): PlanProgressSegment => {
    const count = readStatusCount(counts, status);

    return { status, count, percent: toPercent(count, counts.total) };
  });
};

export const calculatePassedPercent = (counts: PlanProgressCounts): number => {
  return Math.round(toPercent(counts.passed, counts.total));
};

export const selectPlanCaseStatus = (planCase: PlanCase): PlanCaseStatus => {
  return planCase.latestResult?.status ?? "notRun";
};

export const filterPlanCases = (cases: readonly PlanCase[], filter: PlanCaseFilter): PlanCase[] => {
  if (filter === "all") {
    return [...cases];
  }

  return cases.filter((planCase) => {
    return selectPlanCaseStatus(planCase) === filter;
  });
};

export const countPlanCasesByFilter = (
  cases: readonly PlanCase[],
): Record<PlanCaseFilter, number> => {
  const counts: Record<PlanCaseFilter, number> = {
    all: 0,
    passed: 0,
    failed: 0,
    blocked: 0,
    skipped: 0,
    notRun: 0,
  };

  counts.all = cases.length;
  cases.forEach((planCase) => {
    counts[selectPlanCaseStatus(planCase)] += 1;
  });

  return counts;
};

export const selectPlanProgressWindow = (
  plan: Pick<PlanDetail, "signedOffAt" | "closedAt">,
): PlanProgressWindow => {
  if (plan.signedOffAt !== null) {
    return "frozenSignedOff";
  }

  return plan.closedAt === null ? "open" : "frozenClosed";
};
