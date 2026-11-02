import { describe, expect, it } from "vitest";
import { RangeProblem } from "../typing/enums/range-problem.enum";
import {
  buildDefaultRange,
  buildSprintRange,
  countRangeDays,
  findRangeProblem,
  formatIsoDay,
  shiftIsoDay,
} from "./insights-range.util";

const TODAY = new Date("2026-11-02T15:30:00Z");

describe("insights range", () => {
  it("formats and shifts UTC days", () => {
    expect(formatIsoDay(TODAY)).toBe("2026-11-02");
    expect(shiftIsoDay("2026-03-01", -1)).toBe("2026-02-28");
    expect(shiftIsoDay("2026-12-31", 1)).toBe("2027-01-01");
  });

  it("defaults to the last 30 days up to today", () => {
    const range = buildDefaultRange(TODAY);

    expect(range).toEqual({ from: "2026-10-04", to: "2026-11-02" });
    expect(countRangeDays(range)).toBe(30);
  });

  it("finds a start after the end and a range over 366 days", () => {
    expect(findRangeProblem({ from: "2026-11-02", to: "2026-11-01" })).toBe(RangeProblem.ORDER);
    expect(findRangeProblem({ from: "2025-01-01", to: "2026-01-02" })).toBe(RangeProblem.TOO_LONG);
    expect(findRangeProblem({ from: "2025-01-01", to: "2026-01-01" })).toBeNull();
    expect(findRangeProblem({ from: "2026-11-02", to: "2026-11-02" })).toBeNull();
  });

  it("covers a sprint from its start to its end", () => {
    expect(
      buildSprintRange({ startAt: "2026-10-15T08:00:00Z", endAt: "2026-10-29T17:00:00Z" }, TODAY),
    ).toEqual({ from: "2026-10-15", to: "2026-10-29" });
  });

  it("runs a sprint without an end to today and skips one without a start", () => {
    expect(buildSprintRange({ startAt: "2026-10-30T00:00:00Z", endAt: null }, TODAY)).toEqual({
      from: "2026-10-30",
      to: "2026-11-02",
    });
    expect(buildSprintRange({ startAt: null, endAt: "2026-10-29T00:00:00Z" }, TODAY)).toBeNull();
  });

  it("never gives a sprint range that is reversed or too long", () => {
    expect(
      buildSprintRange({ startAt: "2026-10-15T00:00:00Z", endAt: "2026-10-01T00:00:00Z" }, TODAY),
    ).toEqual({ from: "2026-10-15", to: "2026-10-15" });
    const longRange = buildSprintRange(
      { startAt: "2024-01-01T00:00:00Z", endAt: "2026-01-01T00:00:00Z" },
      TODAY,
    );
    expect(longRange).not.toBeNull();
    expect(findRangeProblem(longRange ?? { from: "", to: "" })).toBeNull();
  });
});
