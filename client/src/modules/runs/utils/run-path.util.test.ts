import { describe, expect, it } from "vitest";
import { RunDetailTab } from "../typing/enums/run-detail-tab.enum";
import { buildCasePath, buildRunPath, buildRunsPath, buildStoryPath } from "./run-path.util";

describe("run paths", () => {
  it("builds the runs list path with optional filters", () => {
    expect(buildRunsPath("APP")).toBe("/projects/APP/runs");
    expect(buildRunsPath("APP", { storyKey: "APP-1" })).toBe("/projects/APP/runs?story=APP-1");
    expect(buildRunsPath("APP", { status: "failed", storyKey: "APP-1" })).toBe(
      "/projects/APP/runs?status=failed&story=APP-1",
    );
  });

  it("builds the run path with an optional tab", () => {
    expect(buildRunPath("APP", "r 1")).toBe("/projects/APP/runs/r%201");
    expect(buildRunPath("APP", "r1", RunDetailTab.REPORT)).toBe("/projects/APP/runs/r1?tab=report");
  });

  it("builds the case and story paths", () => {
    expect(buildCasePath("K", "TC-4")).toBe("/projects/K/test-cases/TC-4");
    expect(buildStoryPath("K", "K-12")).toBe("/projects/K/stories/K-12");
    expect(buildStoryPath("K", "K-12", "runs")).toBe("/projects/K/stories/K-12?tab=runs");
  });
});
