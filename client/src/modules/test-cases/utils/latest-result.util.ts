import type {
  CaseLatestResult,
  LatestResult,
} from "@/modules/traceability/typing/types/traceability.type";

export const mapLatestResultByCaseId = (
  caseLatestResults: readonly CaseLatestResult[],
): ReadonlyMap<string, LatestResult | null> => {
  return new Map(
    caseLatestResults.map((caseLatestResult) => {
      return [caseLatestResult.caseId, caseLatestResult.latestResult];
    }),
  );
};
