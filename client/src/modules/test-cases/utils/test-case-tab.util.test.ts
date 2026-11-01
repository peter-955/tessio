import { describe, expect, it } from "vitest";
import { TestCaseDetailTab } from "../typing/enums/test-case-detail-tab.enum";
import { parseTestCaseTab } from "./test-case-tab.util";

describe("parseTestCaseTab", () => {
  it.each([
    ["files", TestCaseDetailTab.FILES],
    ["history", TestCaseDetailTab.HISTORY],
    [["history", "files"], TestCaseDetailTab.HISTORY],
    ["details", TestCaseDetailTab.DETAILS],
    ["runs", TestCaseDetailTab.DETAILS],
    [undefined, TestCaseDetailTab.DETAILS],
  ])("parses %s", (value, expectedTab) => {
    expect(parseTestCaseTab(value)).toBe(expectedTab);
  });
});
