import { describe, expect, it } from "vitest";
import { countReportedCases, listCountEntries } from "./run-counts.util";

const COUNTS = { total: 8, passed: 3, failed: 1, blocked: 0, skipped: 2, notReported: 2 };

describe("listCountEntries", () => {
  it("lists the non-zero counts in a fixed order", () => {
    expect(listCountEntries(COUNTS)).toEqual([
      { key: "passed", count: 3 },
      { key: "failed", count: 1 },
      { key: "skipped", count: 2 },
      { key: "notReported", count: 2 },
    ]);
  });

  it("is empty when nothing was counted", () => {
    expect(
      listCountEntries({ total: 0, passed: 0, failed: 0, blocked: 0, skipped: 0, notReported: 0 }),
    ).toEqual([]);
  });
});

describe("countReportedCases", () => {
  it("adds every recorded status", () => {
    expect(countReportedCases(COUNTS)).toBe(6);
  });
});
