import { describe, expect, it } from "vitest";
import type { TestCaseFilters } from "../typing/types/test-case-filters.type";
import {
  buildTestCaseFiltersSearch,
  buildTestCaseListQuery,
  checkHasTestCaseFilters,
  clearTestCaseFilters,
  EMPTY_TEST_CASE_FILTERS,
  parseTestCaseFilters,
  readTestCaseSearchParams,
} from "./test-case-filters.util";

const CRITERION_ID = "d1000000-0000-4000-8000-000000000001";

const FULL_FILTERS: TestCaseFilters = {
  storyKey: "SHOP-1",
  status: "in_review",
  priority: "high",
  criterionId: CRITERION_ID,
  isNeedingReview: true,
  query: "card",
};

describe("test case filters", () => {
  it("round-trips every filter through the URL", () => {
    const search = buildTestCaseFiltersSearch(FULL_FILTERS);

    expect(search).toBe(
      `?story=SHOP-1&status=in_review&priority=high&criterion=${CRITERION_ID}&needsReview=true&query=card`,
    );
    expect(parseTestCaseFilters(readTestCaseSearchParams(new URLSearchParams(search)))).toEqual(
      FULL_FILTERS,
    );
  });

  it("drops invalid values and uppercases the story key", () => {
    expect(
      parseTestCaseFilters({
        story: "shop-1",
        status: "archived",
        priority: "urgent",
        criterion: "not-a-uuid",
        needsReview: "yes",
        query: ["a".repeat(120), "b"],
      }),
    ).toEqual({ ...EMPTY_TEST_CASE_FILTERS, storyKey: "SHOP-1", query: "a".repeat(100) });
  });

  it("ignores a criterion without a story", () => {
    expect(parseTestCaseFilters({ criterion: CRITERION_ID }).criterionId).toBeNull();
    expect(
      buildTestCaseFiltersSearch({ ...EMPTY_TEST_CASE_FILTERS, criterionId: CRITERION_ID }),
    ).toBe("");
  });

  it("builds the list query without empty values", () => {
    expect(buildTestCaseListQuery({ ...EMPTY_TEST_CASE_FILTERS, query: "  " })).toEqual({});
    expect(buildTestCaseListQuery({ ...FULL_FILTERS, query: " card " })).toEqual({
      storyKey: "SHOP-1",
      status: "in_review",
      priority: "high",
      criterionId: CRITERION_ID,
      needsReview: true,
      query: "card",
    });
  });

  it("knows when filters are set and clears them", () => {
    const storyOnly = { ...EMPTY_TEST_CASE_FILTERS, storyKey: "SHOP-1" };

    expect(checkHasTestCaseFilters(storyOnly, false)).toBe(true);
    expect(checkHasTestCaseFilters(storyOnly, true)).toBe(false);
    expect(clearTestCaseFilters(FULL_FILTERS, true)).toEqual(storyOnly);
    expect(clearTestCaseFilters(FULL_FILTERS, false)).toEqual(EMPTY_TEST_CASE_FILTERS);
  });
});
