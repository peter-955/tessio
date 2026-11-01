import type { Failure, FailureRun, RunStepResult } from "../typing/types/failure.type";

export const findRunStep = (
  run: FailureRun,
  failure: Pick<Failure, "testCaseId" | "latestCaseResultId">,
  order: number,
): RunStepResult | null => {
  const runCase = run.cases.find((candidate) => {
    return (
      candidate.testCaseId === failure.testCaseId &&
      candidate.result?.id === failure.latestCaseResultId
    );
  });

  return (
    runCase?.steps.find((step) => {
      return step.order === order;
    }) ?? null
  );
};
