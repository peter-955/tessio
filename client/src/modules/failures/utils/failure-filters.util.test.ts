import { describe, expect, it } from "vitest";
import { ASSIGNEE_ID, CURRENT_USER_ID } from "../test/utils/failure-fixture.util";
import {
  EMPTY_FAILURE_FILTERS,
  buildFailureFiltersSearch,
  buildFailureListQuery,
  checkHasFailureFilters,
  clearFailureFilters,
  parseFailureFilters,
  readFailureSearchParams,
} from "./failure-filters.util";

describe("failure filters", () => {
  it("defaults to active failures for any person and story", () => {
    expect(parseFailureFilters({})).toEqual(EMPTY_FAILURE_FILTERS);
    expect(buildFailureFiltersSearch(EMPTY_FAILURE_FILTERS)).toBe("");
  });

  it("reads the URL contract and writes it back", () => {
    const searches = ["?assignee=unassigned", "?assignee=me", "?status=all", "?story=TES-1"];

    for (const search of searches) {
      const filters = parseFailureFilters(readFailureSearchParams(new URLSearchParams(search)));

      expect(buildFailureFiltersSearch(filters)).toBe(search);
    }
  });

  it("round trips every filter together", () => {
    const filters = parseFailureFilters({
      status: "verified",
      assignee: ASSIGNEE_ID,
      story: "shop-12",
    });

    expect(filters).toEqual({ status: "verified", assignee: ASSIGNEE_ID, storyKey: "SHOP-12" });
    expect(buildFailureFiltersSearch(filters)).toBe(
      `?status=verified&assignee=${ASSIGNEE_ID}&story=SHOP-12`,
    );
  });

  it("drops unknown values", () => {
    expect(
      parseFailureFilters({ status: "closed", assignee: "somebody", story: "not a key" }),
    ).toEqual(EMPTY_FAILURE_FILTERS);
    expect(parseFailureFilters({ status: ["fixed", "open"] }).status).toBe("fixed");
  });

  it("maps the filters to the list query", () => {
    expect(buildFailureListQuery(EMPTY_FAILURE_FILTERS, CURRENT_USER_ID)).toEqual({
      status: ["open", "fixed", "reopened"],
    });
    expect(
      buildFailureListQuery({ status: "all", assignee: "me", storyKey: null }, CURRENT_USER_ID),
    ).toEqual({ assigneeId: CURRENT_USER_ID });
    expect(
      buildFailureListQuery(
        { status: "fixed", assignee: "unassigned", storyKey: "SHOP-1" },
        CURRENT_USER_ID,
      ),
    ).toEqual({ status: ["fixed"], unassigned: true, storyKey: "SHOP-1" });
    expect(
      buildFailureListQuery(
        { status: "all", assignee: ASSIGNEE_ID, storyKey: null },
        CURRENT_USER_ID,
      ),
    ).toEqual({ assigneeId: ASSIGNEE_ID });
  });

  it("tells when the list is narrowed and clears back to the default", () => {
    expect(checkHasFailureFilters(EMPTY_FAILURE_FILTERS)).toBe(false);
    expect(checkHasFailureFilters({ ...EMPTY_FAILURE_FILTERS, status: "all" })).toBe(false);
    expect(checkHasFailureFilters({ ...EMPTY_FAILURE_FILTERS, status: "verified" })).toBe(true);
    expect(checkHasFailureFilters({ ...EMPTY_FAILURE_FILTERS, assignee: "me" })).toBe(true);
    expect(checkHasFailureFilters({ ...EMPTY_FAILURE_FILTERS, storyKey: "SHOP-1" })).toBe(true);
    expect(clearFailureFilters()).toEqual(EMPTY_FAILURE_FILTERS);
  });
});
