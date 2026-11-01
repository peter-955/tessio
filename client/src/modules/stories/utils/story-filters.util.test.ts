import { describe, expect, it } from "vitest";
import { ACTIVE_SPRINT_ID } from "../test/utils/story-fixture.util";
import type { StoryFilters } from "../typing/types/story-filters.type";
import {
  buildStoryFiltersSearch,
  buildStoryListQuery,
  checkHasStoryFilters,
  parseStoryFilters,
} from "./story-filters.util";

const EMPTY_FILTERS: StoryFilters = { sprintId: null, testStatus: null, query: "" };

describe("parseStoryFilters", () => {
  it("reads valid values from the search params", () => {
    expect(
      parseStoryFilters({ sprint: ACTIVE_SPRINT_ID, status: "in_test", query: "card" }),
    ).toEqual({ sprintId: ACTIVE_SPRINT_ID, testStatus: "in_test", query: "card" });
  });

  it("drops invalid values and takes the first of repeated ones", () => {
    expect(parseStoryFilters({ sprint: "not-a-uuid", status: "done" })).toEqual(EMPTY_FILTERS);
    expect(parseStoryFilters({ status: ["passed", "failed"] })).toEqual({
      ...EMPTY_FILTERS,
      testStatus: "passed",
    });
    expect(parseStoryFilters({ query: "x".repeat(150) }).query).toHaveLength(100);
  });
});

describe("buildStoryListQuery", () => {
  it("leaves out empty values and trims the query", () => {
    expect(buildStoryListQuery({ ...EMPTY_FILTERS, query: "   " })).toEqual({});
    expect(
      buildStoryListQuery({ sprintId: ACTIVE_SPRINT_ID, testStatus: "failed", query: " SHOP " }),
    ).toEqual({ sprintId: ACTIVE_SPRINT_ID, testStatus: "failed", query: "SHOP" });
  });
});

describe("buildStoryFiltersSearch", () => {
  it("returns an empty string without filters", () => {
    expect(buildStoryFiltersSearch(EMPTY_FILTERS)).toBe("");
  });

  it("round-trips through parseStoryFilters", () => {
    const filters: StoryFilters = {
      sprintId: ACTIVE_SPRINT_ID,
      testStatus: "ready_for_test",
      query: "pay & card",
    };
    const search = buildStoryFiltersSearch(filters);

    expect(search).toBe(`?sprint=${ACTIVE_SPRINT_ID}&status=ready_for_test&query=pay+%26+card`);
    expect(parseStoryFilters(Object.fromEntries(new URLSearchParams(search)))).toEqual(filters);
  });
});

describe("checkHasStoryFilters", () => {
  it("ignores a fixed sprint", () => {
    expect(checkHasStoryFilters(EMPTY_FILTERS, false)).toBe(false);
    expect(checkHasStoryFilters({ ...EMPTY_FILTERS, sprintId: ACTIVE_SPRINT_ID }, false)).toBe(
      true,
    );
    expect(checkHasStoryFilters({ ...EMPTY_FILTERS, sprintId: ACTIVE_SPRINT_ID }, true)).toBe(
      false,
    );
    expect(checkHasStoryFilters({ ...EMPTY_FILTERS, query: " a " }, true)).toBe(true);
    expect(checkHasStoryFilters({ ...EMPTY_FILTERS, testStatus: "passed" }, true)).toBe(true);
  });
});
