import { describe, expect, it } from "vitest";
import {
  buildEmptyTrends,
  buildTrendPoint,
  buildTrends,
  SPRINT_ID,
} from "../test/utils/insights-fixture.util";
import type { TrendPoint } from "../typing/types/insights.type";
import {
  buildExecutorData,
  buildExecutorSeries,
  buildFailureData,
  buildGapAgeData,
  buildPassRateData,
  checkTrendsHaveData,
  labelTrendPoint,
} from "./trend-chart.util";

const labelDay = (point: TrendPoint): string => {
  return point.day ?? "";
};

describe("trend charts", () => {
  it("labels a day point by its day and a sprint point by its sprint name", () => {
    expect(labelTrendPoint(buildTrendPoint(), (day) => `day ${day}`)).toBe("day 2026-11-01");
    const sprintPoint = buildTrendPoint({
      day: null,
      sprint: {
        id: SPRINT_ID,
        name: "Sprint 12",
        state: "active",
        startAt: "2026-10-15T00:00:00Z",
        endAt: null,
      },
    });
    expect(labelTrendPoint(sprintPoint, (day) => day)).toBe("Sprint 12");
  });

  it("keeps a missing pass rate as a gap instead of zero", () => {
    expect(
      buildPassRateData([buildTrendPoint(), buildTrendPoint({ passRate: null })], labelDay),
    ).toEqual([
      { category: "2026-11-01", passRate: 75 },
      { category: "2026-11-01", passRate: null },
    ]);
  });

  it("fills every executor of the range, zeros included", () => {
    const point = buildTrendPoint({ runsByExecutor: [{ executor: "claude", count: 3 }] });

    expect(buildExecutorData([point], ["claude", "manual", "ci"], labelDay)).toEqual([
      { category: "2026-11-01", claude: 3, manual: 0, ci: 0 },
    ]);
  });

  it("gives each executor a fixed colour, whatever the other executors", () => {
    const label = (executor: string): string => {
      return executor.toUpperCase();
    };

    expect(buildExecutorSeries(["manual", "ci", "robot"], label)).toEqual([
      { key: "manual", label: "MANUAL", color: "series2" },
      { key: "ci", label: "CI", color: "series4" },
      { key: "robot", label: "ROBOT", color: "series5" },
    ]);
  });

  it("builds failures opened against fixed and gap ages in days", () => {
    expect(buildFailureData([buildTrendPoint()], labelDay)).toEqual([
      { category: "2026-11-01", opened: 1, fixed: 2 },
    ]);
    expect(buildGapAgeData([buildTrendPoint()], labelDay)).toEqual([
      { category: "2026-11-01", medianOpenAge: 2, meanAnswer: 1 },
    ]);
  });

  it("tells whether anything happened in the range", () => {
    expect(checkTrendsHaveData(buildTrends())).toBe(true);
    expect(checkTrendsHaveData(buildEmptyTrends())).toBe(false);
    expect(checkTrendsHaveData(buildTrends({ points: [] }))).toBe(false);
  });
});
