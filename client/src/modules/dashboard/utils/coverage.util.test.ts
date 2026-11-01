import { describe, expect, it } from "vitest";
import { CoverageSegmentKind } from "../typing/enums/coverage-segment-kind.enum";
import type { CoverageCounts } from "../typing/types/dashboard.type";
import { buildCoverageSegments, calculateCoveragePercent } from "./coverage.util";

const buildCoverage = (overrides: Partial<CoverageCounts> = {}): CoverageCounts => {
  return {
    criterionCount: 3,
    coveredCount: 2,
    passedCount: 1,
    failedCount: 0,
    blockedCount: 0,
    notRunCount: 1,
    uncoveredCount: 1,
    ...overrides,
  };
};

describe("calculateCoveragePercent", () => {
  it("returns null when there are no criteria", () => {
    expect(
      calculateCoveragePercent(
        buildCoverage({ criterionCount: 0, coveredCount: 0, uncoveredCount: 0 }),
      ),
    ).toBeNull();
  });

  it("rounds the covered share to a whole percent", () => {
    expect(calculateCoveragePercent(buildCoverage())).toBe(67);
    expect(calculateCoveragePercent(buildCoverage({ criterionCount: 8, coveredCount: 1 }))).toBe(
      13,
    );
    expect(calculateCoveragePercent(buildCoverage({ criterionCount: 4, coveredCount: 4 }))).toBe(
      100,
    );
  });
});

describe("buildCoverageSegments", () => {
  it("keeps the segment order and drops empty segments", () => {
    expect(
      buildCoverageSegments(
        buildCoverage({
          passedCount: 2,
          failedCount: 3,
          blockedCount: 0,
          notRunCount: 1,
          uncoveredCount: 4,
        }),
      ),
    ).toEqual([
      { kind: CoverageSegmentKind.PASSED, count: 2 },
      { kind: CoverageSegmentKind.FAILED, count: 3 },
      { kind: CoverageSegmentKind.NOT_RUN, count: 1 },
      { kind: CoverageSegmentKind.UNCOVERED, count: 4 },
    ]);
  });

  it("returns no segments when every count is zero", () => {
    expect(
      buildCoverageSegments(
        buildCoverage({
          criterionCount: 0,
          coveredCount: 0,
          passedCount: 0,
          notRunCount: 0,
          uncoveredCount: 0,
        }),
      ),
    ).toEqual([]);
  });
});
