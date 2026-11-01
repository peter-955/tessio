import type { CoverageHighlight } from "../typing/types/coverage-highlight.type";
import type { CoverageCount } from "../typing/types/traceability.type";

export const selectCoverageHighlight = (coverage: CoverageCount): CoverageHighlight | null => {
  if (coverage.failedCount > 0) {
    return { kind: "failing", count: coverage.failedCount };
  }

  if (coverage.blockedCount > 0) {
    return { kind: "blocked", count: coverage.blockedCount };
  }

  if (coverage.uncoveredCount > 0) {
    return { kind: "uncovered", count: coverage.uncoveredCount };
  }

  if (coverage.criterionCount > 0 && coverage.passedCount === coverage.criterionCount) {
    return { kind: "allPassing", count: coverage.passedCount };
  }

  return null;
};
