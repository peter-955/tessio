import { describe, expect, it } from "vitest";
import {
  buildDashboardSearch,
  parseDashboardSprintId,
  readDashboardSearchParams,
} from "./dashboard-search.util";

const SPRINT_ID = "5a1e2b3c-4d5e-4f60-8a1b-2c3d4e5f6a70";
const OTHER_SPRINT_ID = "7c3a4d5e-6f7a-4b82-8c3d-4e5f6a7b8c92";

describe("parseDashboardSprintId", () => {
  it("keeps a valid sprint id", () => {
    expect(parseDashboardSprintId({ sprint: SPRINT_ID })).toBe(SPRINT_ID);
  });

  it("ignores a missing or malformed sprint id", () => {
    expect(parseDashboardSprintId({})).toBeNull();
    expect(parseDashboardSprintId({ sprint: "sprint-12" })).toBeNull();
    expect(parseDashboardSprintId({ sprint: "" })).toBeNull();
  });

  it("takes the first value of a repeated parameter", () => {
    expect(parseDashboardSprintId({ sprint: [SPRINT_ID, OTHER_SPRINT_ID] })).toBe(SPRINT_ID);
    expect(parseDashboardSprintId({ sprint: ["bad", SPRINT_ID] })).toBeNull();
  });
});

describe("readDashboardSearchParams", () => {
  it("turns URL search params into a record", () => {
    expect(
      readDashboardSearchParams(
        new URLSearchParams(`sprint=${SPRINT_ID}&sprint=${OTHER_SPRINT_ID}&tab=runs`),
      ),
    ).toEqual({ sprint: [SPRINT_ID, OTHER_SPRINT_ID], tab: "runs" });
  });
});

describe("buildDashboardSearch", () => {
  it("builds an empty search for the current sprint", () => {
    expect(buildDashboardSearch(null)).toBe("");
  });

  it("puts the sprint id in the search", () => {
    expect(buildDashboardSearch(SPRINT_ID)).toBe(`?sprint=${SPRINT_ID}`);
  });
});
