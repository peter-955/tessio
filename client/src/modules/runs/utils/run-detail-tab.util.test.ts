import { describe, expect, it } from "vitest";
import { RunDetailTab } from "../typing/enums/run-detail-tab.enum";
import { parseRunDetailTab } from "./run-detail-tab.util";

describe("parseRunDetailTab", () => {
  it("accepts a known tab", () => {
    expect(parseRunDetailTab("report")).toBe(RunDetailTab.REPORT);
    expect(parseRunDetailTab(["report", "results"])).toBe(RunDetailTab.REPORT);
  });

  it("falls back to the results tab", () => {
    expect(parseRunDetailTab(undefined)).toBe(RunDetailTab.RESULTS);
    expect(parseRunDetailTab(null)).toBe(RunDetailTab.RESULTS);
    expect(parseRunDetailTab("history")).toBe(RunDetailTab.RESULTS);
  });
});
