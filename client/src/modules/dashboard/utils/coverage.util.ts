import {
  COVERAGE_SEGMENT_COUNT_FIELDS,
  COVERAGE_SEGMENT_ORDER,
} from "../typing/constants/dashboard.constant";
import type { CoverageCounts, CoverageSegment } from "../typing/types/dashboard.type";

const PERCENT_SCALE = 100;

export const calculateCoveragePercent = (coverage: CoverageCounts): number | null => {
  if (coverage.criterionCount === 0) {
    return null;
  }

  return Math.round((coverage.coveredCount / coverage.criterionCount) * PERCENT_SCALE);
};

export const buildCoverageSegments = (coverage: CoverageCounts): CoverageSegment[] => {
  return COVERAGE_SEGMENT_ORDER.map((kind) => {
    return { kind, count: coverage[COVERAGE_SEGMENT_COUNT_FIELDS[kind]] };
  }).filter((segment) => {
    return segment.count > 0;
  });
};
