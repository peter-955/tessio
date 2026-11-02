import { describe, expect, it } from "vitest";
import {
  EMPTY_RUN_FILTERS,
  buildRunFiltersSearch,
  buildRunListQuery,
  checkHasRunFilters,
  parseRunFilters,
  readRunSearchParams,
} from "./run-filters.util";

describe("parseRunFilters", () => {
  it("keeps a known status and an uppercased valid story key", () => {
    expect(parseRunFilters({ status: "failed", story: "app-12" })).toEqual({
      status: "failed",
      storyKey: "APP-12",
      suiteId: null,
    });
  });

  it("keeps a valid suite id in lower case and drops an invalid one", () => {
    expect(parseRunFilters({ suite: "5A000000-0000-4000-8000-000000000001" })).toEqual({
      ...EMPTY_RUN_FILTERS,
      suiteId: "5a000000-0000-4000-8000-000000000001",
    });
    expect(parseRunFilters({ suite: "smoke" })).toEqual(EMPTY_RUN_FILTERS);
  });

  it("drops an unknown status and an invalid story key", () => {
    expect(parseRunFilters({ status: "queued", story: "not a key" })).toEqual(EMPTY_RUN_FILTERS);
    expect(parseRunFilters({ story: "APP-0" })).toEqual(EMPTY_RUN_FILTERS);
  });

  it("reads the first value of repeated parameters", () => {
    expect(parseRunFilters({ status: ["aborted", "passed"] })).toEqual({
      status: "aborted",
      storyKey: null,
      suiteId: null,
    });
  });
});

describe("buildRunFiltersSearch", () => {
  it("returns an empty search without filters", () => {
    expect(buildRunFiltersSearch(EMPTY_RUN_FILTERS)).toBe("");
  });

  it("writes the status and the story", () => {
    expect(buildRunFiltersSearch({ status: "failed", storyKey: "APP-1", suiteId: null })).toBe(
      "?status=failed&story=APP-1",
    );
  });

  it("writes the suite", () => {
    expect(
      buildRunFiltersSearch({
        ...EMPTY_RUN_FILTERS,
        suiteId: "5a000000-0000-4000-8000-000000000001",
      }),
    ).toBe("?suite=5a000000-0000-4000-8000-000000000001");
  });
});

describe("buildRunListQuery", () => {
  it("always sends the limit", () => {
    expect(buildRunListQuery(EMPTY_RUN_FILTERS)).toEqual({ limit: 50 });
    expect(buildRunListQuery({ status: "running", storyKey: "APP-3", suiteId: null })).toEqual({
      status: "running",
      storyKey: "APP-3",
      limit: 50,
    });
    expect(
      buildRunListQuery({ ...EMPTY_RUN_FILTERS, suiteId: "5a000000-0000-4000-8000-000000000001" }),
    ).toEqual({ suiteId: "5a000000-0000-4000-8000-000000000001", limit: 50 });
  });
});

describe("readRunSearchParams", () => {
  it("turns URL search params into a record", () => {
    expect(readRunSearchParams(new URLSearchParams("status=failed&story=A-1&story=A-2"))).toEqual({
      status: "failed",
      story: ["A-1", "A-2"],
    });
  });
});

describe("checkHasRunFilters", () => {
  it("is true when any filter is set", () => {
    expect(checkHasRunFilters(EMPTY_RUN_FILTERS)).toBe(false);
    expect(checkHasRunFilters({ status: null, storyKey: "APP-1", suiteId: null })).toBe(true);
    expect(
      checkHasRunFilters({ ...EMPTY_RUN_FILTERS, suiteId: "5a000000-0000-4000-8000-000000000001" }),
    ).toBe(true);
  });
});
