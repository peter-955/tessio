import { describe, expect, it } from "vitest";
import { buildSuiteDetail } from "../test/utils/suite.fixture";
import { EMPTY_SUITE_FILTER_VALUES } from "../typing/constants/suite.constant";
import { checkIsSuiteDescriptionTooLong, findSuiteNameError } from "./suite-form.util";
import {
  buildCreateSuiteRequest,
  buildSuiteFilterRequest,
  buildUpdateSuiteRequest,
  checkHasSuiteFilter,
} from "./suite-request.util";

describe("suite form requests", () => {
  it("trims the name and turns a blank description into none", () => {
    expect(buildCreateSuiteRequest({ name: "  Smoke ", description: "   " })).toEqual({
      name: "Smoke",
      description: null,
    });
  });

  it("sends only the fields that changed", () => {
    const suite = buildSuiteDetail();

    expect(
      buildUpdateSuiteRequest({ name: suite.name, description: suite.description ?? "" }, suite),
    ).toEqual({});
    expect(buildUpdateSuiteRequest({ name: "Smoke", description: "" }, suite)).toEqual({
      name: "Smoke",
      description: null,
    });
  });

  it("checks the name and the description length", () => {
    expect(findSuiteNameError("   ")).toBe("required");
    expect(findSuiteNameError("a".repeat(121))).toBe("tooLong");
    expect(findSuiteNameError("a".repeat(120))).toBeNull();
    expect(checkIsSuiteDescriptionTooLong("a".repeat(2001))).toBe(true);
    expect(checkIsSuiteDescriptionTooLong("a".repeat(2000))).toBe(false);
  });
});

describe("suite filter requests", () => {
  it("needs at least one filter", () => {
    expect(checkHasSuiteFilter(EMPTY_SUITE_FILTER_VALUES)).toBe(false);
    expect(checkHasSuiteFilter({ ...EMPTY_SUITE_FILTER_VALUES, sprintId: "s1" })).toBe(true);
  });

  it("sends only the filters that are set", () => {
    expect(
      buildSuiteFilterRequest({
        ...EMPTY_SUITE_FILTER_VALUES,
        labels: ["smoke"],
        storyKey: "SHOP-1",
      }),
    ).toEqual({ labels: ["smoke"], storyKey: "SHOP-1" });
  });
});
