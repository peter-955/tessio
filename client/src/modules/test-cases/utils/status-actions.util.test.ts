import { describe, expect, it } from "vitest";
import { TEST_CASE_STATUS_TRANSITIONS } from "../typing/constants/test-case.constant";
import type { TestCaseStatus } from "../typing/types/test-case.type";
import { buildTestCaseStatusActions, checkCanChangeTestCaseStatus } from "./status-actions.util";

describe("buildTestCaseStatusActions", () => {
  it("offers Submit for review on a draft and Deprecate in the menu", () => {
    expect(buildTestCaseStatusActions("draft")).toEqual({
      primary: { status: "in_review", label: "submitForReview" },
      secondary: [{ status: "deprecated", label: "deprecate" }],
    });
  });

  it("offers Mark ready while in review", () => {
    expect(buildTestCaseStatusActions("in_review")).toEqual({
      primary: { status: "ready", label: "markReady" },
      secondary: [
        { status: "draft", label: "backToDraft" },
        { status: "deprecated", label: "deprecate" },
      ],
    });
  });

  it("keeps every ready action in the menu", () => {
    expect(buildTestCaseStatusActions("ready")).toEqual({
      primary: null,
      secondary: [
        { status: "in_review", label: "backToReview" },
        { status: "draft", label: "backToDraft" },
        { status: "deprecated", label: "deprecate" },
      ],
    });
  });

  it("only restores a deprecated case", () => {
    expect(buildTestCaseStatusActions("deprecated")).toEqual({
      primary: { status: "draft", label: "restore" },
      secondary: [],
    });
  });

  it("never offers a transition outside the table", () => {
    const statuses = Object.keys(TEST_CASE_STATUS_TRANSITIONS) as TestCaseStatus[];

    for (const status of statuses) {
      const { primary, secondary } = buildTestCaseStatusActions(status);
      const offered = [...(primary === null ? [] : [primary]), ...secondary].map(
        (action) => action.status,
      );

      expect([...offered].sort()).toEqual([...TEST_CASE_STATUS_TRANSITIONS[status]].sort());
      expect(offered.every((target) => checkCanChangeTestCaseStatus(status, target))).toBe(true);
    }
  });
});
