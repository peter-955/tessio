import type { SkipReason, SuiteCase } from "../typing/types/suite.type";

export const listSuiteCaseIds = (cases: readonly SuiteCase[]): string[] => {
  return cases.map((suiteCase) => {
    return suiteCase.testCaseId;
  });
};

export const moveCaseId = (
  caseIds: readonly string[],
  fromIndex: number,
  toIndex: number,
): string[] => {
  const movingId = caseIds[fromIndex];
  if (movingId === undefined || toIndex < 0 || toIndex >= caseIds.length) {
    return [...caseIds];
  }

  const remainingIds = caseIds.filter((_, index) => {
    return index !== fromIndex;
  });

  return [...remainingIds.slice(0, toIndex), movingId, ...remainingIds.slice(toIndex)];
};

export const removeCaseId = (caseIds: readonly string[], caseId: string): string[] => {
  return caseIds.filter((id) => {
    return id !== caseId;
  });
};

export const appendCaseIds = (
  caseIds: readonly string[],
  addedIds: readonly string[],
): string[] => {
  const knownIds = new Set(caseIds);

  return [
    ...caseIds,
    ...addedIds.filter((id) => {
      if (knownIds.has(id)) {
        return false;
      }

      knownIds.add(id);

      return true;
    }),
  ];
};

export const orderSuiteCases = (
  cases: readonly SuiteCase[],
  caseIds: readonly string[],
): SuiteCase[] => {
  const casesById = new Map(
    cases.map((suiteCase) => {
      return [suiteCase.testCaseId, suiteCase];
    }),
  );

  return caseIds.flatMap((caseId) => {
    const suiteCase = casesById.get(caseId);

    return suiteCase === undefined ? [] : [suiteCase];
  });
};

export const findSuiteCaseSkipReason = (suiteCase: SuiteCase): SkipReason | null => {
  if (suiteCase.status !== "ready") {
    return "not_ready";
  }

  return suiteCase.isNeedingReview ? "needs_review" : null;
};

export const listRunnableSuiteCases = (cases: readonly SuiteCase[]): SuiteCase[] => {
  return cases.filter((suiteCase) => {
    return suiteCase.isRunnable;
  });
};

export const listSkippedSuiteCases = (cases: readonly SuiteCase[]): SuiteCase[] => {
  return cases.filter((suiteCase) => {
    return !suiteCase.isRunnable;
  });
};
