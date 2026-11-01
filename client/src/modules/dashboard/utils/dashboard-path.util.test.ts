import { describe, expect, it } from "vitest";
import {
  buildCaseHref,
  buildFailureHref,
  buildFailuresHref,
  buildNewCaseHref,
  buildRunHref,
  buildRunsHref,
  buildSprintStoriesHref,
  buildStoryHref,
  buildUnassignedFailuresHref,
} from "./dashboard-path.util";

const SPRINT_ID = "5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70";

describe("dashboard paths", () => {
  it("builds the filtered stories list", () => {
    expect(buildSprintStoriesHref("SHOP", SPRINT_ID, "in_test")).toBe(
      `/projects/SHOP/stories?sprint=${SPRINT_ID}&status=in_test`,
    );
    expect(buildSprintStoriesHref("SHOP", SPRINT_ID, null)).toBe(
      `/projects/SHOP/stories?sprint=${SPRINT_ID}`,
    );
    expect(buildSprintStoriesHref("SHOP", null, null)).toBe("/projects/SHOP/stories");
  });

  it("encodes every path part", () => {
    expect(buildStoryHref("SH/OP", "SHOP 1")).toBe("/projects/SH%2FOP/stories/SHOP%201");
    expect(buildCaseHref("SHOP", "TC/7")).toBe("/projects/SHOP/test-cases/TC%2F7");
    expect(buildNewCaseHref("SHOP", "SHOP&1")).toBe("/projects/SHOP/test-cases/new?story=SHOP%261");
    expect(buildFailureHref("SHOP", "f/1")).toBe("/projects/SHOP/failures/f%2F1");
    expect(buildRunHref("SH OP", "r1")).toBe("/projects/SH%20OP/runs/r1");
  });

  it("builds the failure and run lists", () => {
    expect(buildFailuresHref("SHOP")).toBe("/projects/SHOP/failures");
    expect(buildUnassignedFailuresHref("SHOP")).toBe("/projects/SHOP/failures?assignee=unassigned");
    expect(buildRunsHref("SHOP")).toBe("/projects/SHOP/runs");
  });
});
