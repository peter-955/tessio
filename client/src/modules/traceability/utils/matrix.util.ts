import type { DSTraceabilityCase, DSTraceabilityCriterion } from "@/components/design-system";
import { buildTestCasePath } from "@/modules/test-cases/utils/test-case-path.util";
import type { MatrixCaseLabels } from "../typing/types/matrix-case-labels.type";
import type { CriterionTrace, TracedCase } from "../typing/types/traceability.type";

const listCaseMarkers = (tracedCase: TracedCase, labels: MatrixCaseLabels): string[] => {
  const markers: string[] = [];

  if (tracedCase.status === "draft" || tracedCase.status === "in_review") {
    markers.push(labels.notReady[tracedCase.status]);
  }

  if (tracedCase.needsReview) {
    markers.push(labels.needsReview);
  }

  return markers;
};

export const buildMatrixCases = (
  cases: readonly TracedCase[],
  projectKey: string,
  labels: MatrixCaseLabels,
): DSTraceabilityCase[] => {
  return cases.map((tracedCase): DSTraceabilityCase => {
    return {
      id: tracedCase.id,
      code: tracedCase.code,
      title: tracedCase.title,
      href: buildTestCasePath(projectKey, tracedCase.code),
      resultStatus: tracedCase.latestResult?.status ?? "not_run",
      markers: listCaseMarkers(tracedCase, labels),
    };
  });
};

export const buildMatrixCriteria = (
  criteria: readonly CriterionTrace[],
  formatRemoved: (removedAt: string) => string,
): DSTraceabilityCriterion[] => {
  return criteria.map((criterion): DSTraceabilityCriterion => {
    return {
      id: criterion.id,
      code: criterion.code,
      text: criterion.text,
      status: criterion.status,
      removedLabel: criterion.removedAt === null ? null : formatRemoved(criterion.removedAt),
      linkedCaseIds: criterion.linkedCaseIds,
    };
  });
};

export const listUncoveredCriteria = (criteria: readonly CriterionTrace[]): CriterionTrace[] => {
  return criteria.filter((criterion) => {
    return criterion.removedAt === null && criterion.status === "uncovered";
  });
};
