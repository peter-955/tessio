import { describe, expect, it } from "vitest";
import { checkIsUntargetedRun } from "./run-target.util";

const STORY_ID = "c6000000-0000-4000-8000-000000000001";
const SUITE_ID = "5a000000-0000-4000-8000-000000000001";

describe("checkIsUntargetedRun", () => {
  it("is true for a CI import without a story or suite", () => {
    expect(checkIsUntargetedRun({ storyId: null, testSuiteId: null })).toBe(true);
    expect(checkIsUntargetedRun({ storyId: null })).toBe(true);
  });

  it("is false for a story run or a suite run", () => {
    expect(checkIsUntargetedRun({ storyId: STORY_ID, testSuiteId: null })).toBe(false);
    expect(checkIsUntargetedRun({ storyId: null, testSuiteId: SUITE_ID })).toBe(false);
  });
});
