import type { ResultStatus, RunCase, RunStatus } from "@/shared/typing/types/test-run.type";
import type { ResultOutcome } from "../typing/types/run.type";

export const resolveCaseOutcome = (
  result: RunCase["result"],
  runStatus: RunStatus,
): ResultOutcome => {
  if (result !== null) {
    return result.status;
  }

  return runStatus === "running" ? "pending" : "not_reported";
};

export const resolveStepOutcome = (
  stepStatus: ResultStatus | null,
  caseOutcome: ResultOutcome,
): ResultOutcome => {
  if (stepStatus !== null) {
    return stepStatus;
  }

  return caseOutcome === "pending" ? "pending" : "not_reported";
};
