import {
  FALLBACK_RESULT_STATUS,
  SUGGESTION_PRIORITY,
} from "../typing/constants/result-status.constant";
import type { ResultStatus } from "../typing/types/manual-run.type";

export const suggestCaseStatus = (statuses: readonly (ResultStatus | null)[]): ResultStatus => {
  return (
    SUGGESTION_PRIORITY.find((status) => {
      return statuses.includes(status);
    }) ?? FALLBACK_RESULT_STATUS
  );
};
