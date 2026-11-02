import { describe, expect, it } from "vitest";
import {
  buildLabelCoverage,
  buildSprintCoverage,
  buildTokenRun,
} from "../test/utils/insights-fixture.util";
import { buildLabelCoverageData, listLabelCoverageRows } from "./label-coverage.util";
import { buildSprintCoverageData, checkSprintCoverageHasCriteria } from "./sprint-coverage.util";
import { buildTokenChartData, describeTokenRunSource } from "./token-usage.util";

describe("coverage by label", () => {
  it("adds the unlabelled cases after the labels", () => {
    const rows = listLabelCoverageRows(buildLabelCoverage(), "No label");

    expect(
      rows.map((row) => {
        return row.name;
      }),
    ).toEqual(["checkout", "No label"]);
    expect(buildLabelCoverageData(rows)).toEqual([
      { category: "checkout", ready: 75, passed: 50 },
      { category: "No label", ready: 50, passed: 0 },
    ]);
  });

  it("leaves the unlabelled row out when every case has a label", () => {
    const report = buildLabelCoverage();
    report.unlabelled = {
      caseCount: 0,
      readyCount: 0,
      passedCount: 0,
      readyShare: null,
      passedShare: null,
    };

    expect(listLabelCoverageRows(report, "No label")).toHaveLength(1);
  });
});

describe("AC coverage per sprint", () => {
  it("stacks the criteria of each sprint by state", () => {
    expect(buildSprintCoverageData([buildSprintCoverage()])).toEqual([
      { category: "Sprint 12", passed: 5, failed: 1, blocked: 1, notRun: 1, uncovered: 2 },
    ]);
  });

  it("is empty when no sprint has criteria", () => {
    const empty = buildSprintCoverage();
    empty.coverage = { ...empty.coverage, criterionCount: 0 };

    expect(checkSprintCoverageHasCriteria([empty])).toBe(false);
    expect(checkSprintCoverageHasCriteria([])).toBe(false);
    expect(checkSprintCoverageHasCriteria([buildSprintCoverage()])).toBe(true);
  });
});

describe("tokens per run", () => {
  it("names a run by its story, or its suite for a suite run", () => {
    expect(describeTokenRunSource(buildTokenRun())).toBe("SHOP-1");
    expect(
      describeTokenRunSource(buildTokenRun({ storyJiraKey: null, testSuiteName: "Smoke" })),
    ).toBe("Smoke");
  });

  it("charts the newest runs from oldest to newest", () => {
    const runs = Array.from({ length: 35 }, (_, index) => {
      return buildTokenRun({ runId: `run-${String(index)}`, inputTokens: index });
    });
    const data = buildTokenChartData(runs, (run) => {
      return run.runId;
    });

    expect(data).toHaveLength(30);
    expect(data[0]).toMatchObject({ category: "run-29", input: 29 });
    expect(data[29]).toMatchObject({
      category: "run-0",
      input: 0,
      cacheWrite: 200,
      cacheRead: 3000,
      output: 800,
    });
  });
});
