import type { ManualRunCase } from "../typing/types/manual-run.type";

export const checkIsDataDrivenCase = (runCase: ManualRunCase): boolean => {
  return runCase.iterations.length > 0;
};

export const countRecordedIterations = (runCase: ManualRunCase): number => {
  return runCase.iterations.filter((iteration) => iteration.result !== null).length;
};

export const checkIsCaseRecorded = (runCase: ManualRunCase): boolean => {
  return checkIsDataDrivenCase(runCase)
    ? countRecordedIterations(runCase) === runCase.iterations.length
    : runCase.result !== null;
};

export const findFirstUnrecordedIteration = (runCase: ManualRunCase): number | null => {
  return runCase.iterations.find((iteration) => iteration.result === null)?.iteration ?? null;
};

export const findNextUnrecordedIteration = (
  runCase: ManualRunCase,
  currentIteration: number,
): number | null => {
  const unrecorded = runCase.iterations.filter((iteration) => iteration.result === null);

  return (
    unrecorded.find((iteration) => iteration.iteration > currentIteration)?.iteration ??
    unrecorded.find((iteration) => iteration.iteration !== currentIteration)?.iteration ??
    null
  );
};

export const sortRunCases = (cases: readonly ManualRunCase[]): ManualRunCase[] => {
  return [...cases].sort((first, second) => {
    return first.position - second.position;
  });
};

export const countRecordedCases = (cases: readonly ManualRunCase[]): number => {
  return cases.filter((runCase) => {
    return checkIsCaseRecorded(runCase);
  }).length;
};

export const findFirstUnrecordedCase = (cases: readonly ManualRunCase[]): ManualRunCase | null => {
  return (
    sortRunCases(cases).find((runCase) => {
      return !checkIsCaseRecorded(runCase);
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
      return !checkIsCaseRecorded(runCase);
    }) ?? null
  );
};
