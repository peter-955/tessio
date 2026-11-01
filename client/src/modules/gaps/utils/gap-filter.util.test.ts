import { describe, expect, it } from "vitest";
import { createGap, createResolvedGap } from "../test/utils/gap.fixture";
import { countGapsByFilter, countOpenGaps, filterGapsByStatus } from "./gap-filter.util";

const OPEN_GAP = createGap();
const SECOND_OPEN_GAP = createGap({ id: "b1000000-0000-4000-8000-000000000002" });
const RESOLVED_GAP = createResolvedGap();
const GAPS = [OPEN_GAP, RESOLVED_GAP, SECOND_OPEN_GAP];

describe("gap filters", () => {
  it("keeps the gaps of the chosen status in order", () => {
    expect(filterGapsByStatus(GAPS, "open")).toEqual([OPEN_GAP, SECOND_OPEN_GAP]);
    expect(filterGapsByStatus(GAPS, "resolved")).toEqual([RESOLVED_GAP]);
    expect(filterGapsByStatus(GAPS, "all")).toEqual(GAPS);
  });

  it("counts the open gaps and every filter", () => {
    expect(countOpenGaps(GAPS)).toBe(2);
    expect(countOpenGaps([])).toBe(0);
    expect(countGapsByFilter(GAPS)).toEqual({ open: 2, resolved: 1, all: 3 });
  });
});
