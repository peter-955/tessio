import { describe, expect, it } from "vitest";
import { TestDataTab } from "../typing/enums/test-data-tab.enum";
import { parseTestDataTab } from "./test-data-tab.util";

describe("parseTestDataTab", () => {
  it("reads a known tab", () => {
    expect(parseTestDataTab("environments")).toBe(TestDataTab.ENVIRONMENTS);
    expect(parseTestDataTab("data")).toBe(TestDataTab.DATA);
  });

  it("uses the first value of a repeated parameter", () => {
    expect(parseTestDataTab(["environments", "data"])).toBe(TestDataTab.ENVIRONMENTS);
  });

  it.each([undefined, "", "unknown", []])("defaults to the data tab for %s", (value) => {
    expect(parseTestDataTab(value)).toBe(TestDataTab.DATA);
  });
});
