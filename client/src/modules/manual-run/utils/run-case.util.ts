import type { ManualRunCase } from "../typing/types/manual-run.type";

export const sortRunCases = (cases: readonly ManualRunCase[]): ManualRunCase[] => {
  return [...cases].sort((first, second) => {
    return first.position - second.position;
  });
};

export const countRecordedCases = (cases: readonly ManualRunCase[]): number => {
  return cases.filter((runCase) => {
    return runCase.result !== null;
  }).length;
};

export const findFirstUnrecordedCase = (cases: readonly ManualRunCase[]): ManualRunCase | null => {
  return (
    sortRunCases(cases).find((runCase) => {
      return runCase.result === null;
    }) ?? null
  );
};

export const findNextUnrecordedCase = (
  cases: readonly ManualRunCase[],
  currentTestCaseId: string,
): ManualRunCase | null => {
  const sortedCases = sortRunCases(cases);
  const currentIndex = sortedCases.findIndex((runCase) => {
    return runCase.testCaseId === currentTestCaseId;
  });
  const casesAfterCurrent = sortedCases.slice(currentIndex + 1);
  const casesBeforeCurrent = currentIndex < 0 ? [] : sortedCases.slice(0, currentIndex);

  return (
    [...casesAfterCurrent, ...casesBeforeCurrent].find((runCase) => {
      return runCase.result === null;
    }) ?? null
  );
};
