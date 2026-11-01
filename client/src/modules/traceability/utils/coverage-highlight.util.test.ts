import { describe, expect, it } from "vitest";
import { buildCoverageCount } from "../test/utils/traceability-fixture.util";
import { selectCoverageHighlight } from "./coverage-highlight.util";

describe("selectCoverageHighlight", () => {
  it("shows failing first", () => {
    expect(
      selectCoverageHighlight(buildCoverageCount({ failedCount: 2, blockedCount: 1 })),
    ).toEqual({ kind: "failing", count: 2 });
  });

  it("shows blocked when nothing fails", () => {
    expect(
      selectCoverageHighlight(buildCoverageCount({ failedCount: 0, blockedCount: 1 })),
    ).toEqual({ kind: "blocked", count: 1 });
  });

  it("shows uncovered when nothing fails or is blocked", () => {
    expect(selectCoverageHighlight(buildCoverageCount({ failedCount: 0 }))).toEqual({
      kind: "uncovered",
      count: 1,
    });
  });

  it("shows all passing when every criterion passed", () => {
    expect(
      selectCoverageHighlight(
        buildCoverageCount({
          criterionCount: 2,
          coveredCount: 2,
          passedCount: 2,
          failedCount: 0,
          notRunCount: 0,
          uncoveredCount: 0,
        }),
      ),
    ).toEqual({ kind: "allPassing", count: 2 });
  });

  it("shows nothing when cases are only not run or there are no criteria", () => {
    expect(
      selectCoverageHighlight(
        buildCoverageCount({ failedCount: 0, uncoveredCount: 0, passedCount: 1 }),
      ),
    ).toBeNull();
    expect(
      selectCoverageHighlight(
        buildCoverageCount({
          criterionCount: 0,
          coveredCount: 0,
          failedCount: 0,
          notRunCount: 0,
          uncoveredCount: 0,
        }),
      ),
    ).toBeNull();
  });
});
