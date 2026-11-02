import { describe, expect, it } from "vitest";
import { PLAN_CASES, buildCounts, buildPlanCase } from "../test/utils/plan-fixture.util";
import {
  buildProgressSegments,
  calculatePassedPercent,
  countPlanCasesByFilter,
  filterPlanCases,
  selectPlanCaseStatus,
  selectPlanProgressWindow,
} from "./plan-progress.util";

describe("plan progress utils", () => {
  it("builds one segment per result status, as a share of every case", () => {
    const segments = buildProgressSegments(
      buildCounts({ total: 8, passed: 4, failed: 2, blocked: 1, notRun: 1 }),
    );

    expect(segments).toEqual([
      { status: "passed", count: 4, percent: 50 },
      { status: "failed", count: 2, percent: 25 },
      { status: "blocked", count: 1, percent: 12.5 },
      { status: "skipped", count: 0, percent: 0 },
    ]);
  });

  it("gives empty segments and 0% for a plan with no case", () => {
    const counts = buildCounts();

    expect(
      buildProgressSegments(counts).every((segment) => {
        return segment.percent === 0;
      }),
    ).toBe(true);
    expect(calculatePassedPercent(counts)).toBe(0);
  });

  it("rounds the passed share to a whole percent", () => {
    expect(calculatePassedPercent(buildCounts({ total: 3, passed: 2, notRun: 1 }))).toBe(67);
  });

  it("treats a case with no latest result as not run", () => {
    expect(selectPlanCaseStatus(buildPlanCase({ latestResult: null }))).toBe("notRun");
    expect(selectPlanCaseStatus(buildPlanCase())).toBe("passed");
  });

  it("filters and counts the cases by status", () => {
    expect(
      filterPlanCases(PLAN_CASES, "failed").map((planCase) => {
        return planCase.code;
      }),
    ).toEqual(["TC-2"]);
    expect(filterPlanCases(PLAN_CASES, "all")).toHaveLength(3);
    expect(countPlanCasesByFilter(PLAN_CASES)).toEqual({
      all: 3,
      passed: 1,
      failed: 1,
      blocked: 0,
      skipped: 0,
      notRun: 1,
    });
  });

  it("names the result window by the plan's sign-off and close", () => {
    expect(selectPlanProgressWindow({ signedOffAt: null, closedAt: null })).toBe("open");
    expect(
      selectPlanProgressWindow({
        signedOffAt: "2026-11-02T10:00:00Z",
        closedAt: "2026-11-03T10:00:00Z",
      }),
    ).toBe("frozenSignedOff");
    expect(selectPlanProgressWindow({ signedOffAt: null, closedAt: "2026-11-03T10:00:00Z" })).toBe(
      "frozenClosed",
    );
  });
});
