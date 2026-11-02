import {
  buildTestCaseDetail,
  QC_USER_ID,
} from "@/modules/test-cases/test/utils/test-case-fixture.util";
import { buildTestCaseStatusActions } from "@/modules/test-cases/utils/status-actions.util";
import { describe, expect, it } from "vitest";
import {
  buildResolvedComment,
  buildReviewComment,
  REVIEWER_ID,
} from "../test/utils/review-comment-fixture.util";
import {
  checkIsAuthorReviewBlocked,
  countOpenReviewComments,
  groupReviewComments,
  parseStepTarget,
  removeReadyAction,
  truncateText,
} from "./review-comment.util";

describe("review comment utils", () => {
  it("splits comments into open and resolved, keeping their order", () => {
    const first = buildReviewComment({ id: "first" });
    const resolved = buildResolvedComment();
    const second = buildReviewComment({ id: "second" });

    expect(groupReviewComments([first, resolved, second])).toEqual({
      open: [first, second],
      resolved: [resolved],
    });
  });

  it("counts open comments and treats a missing list as none", () => {
    expect(countOpenReviewComments([buildReviewComment(), buildResolvedComment()])).toBe(1);
    expect(countOpenReviewComments(undefined)).toBe(0);
  });

  it.each([
    [true, QC_USER_ID, true],
    [true, REVIEWER_ID, false],
    [true, null, false],
    [false, QC_USER_ID, false],
  ])(
    "blocks the author only when the setting is %s and the user is %s",
    (requireSeparateReviewer, userId, isBlocked) => {
      const detail = buildTestCaseDetail();

      expect(checkIsAuthorReviewBlocked({ requireSeparateReviewer }, detail, userId)).toBe(
        isBlocked,
      );
    },
  );

  it("removes the Ready action and keeps the other moves", () => {
    const actions = removeReadyAction(buildTestCaseStatusActions("in_review"));

    expect(actions.primary).toBeNull();
    expect(actions.secondary.map((action) => action.status)).toEqual(["draft", "deprecated"]);
  });

  it("leaves actions without Ready unchanged", () => {
    const actions = buildTestCaseStatusActions("draft");

    expect(removeReadyAction(actions)).toEqual(actions);
  });

  it.each([
    ["case", null],
    ["2", 2],
    ["0", null],
    ["two", null],
  ])("parses the comment target %s", (target, stepOrder) => {
    expect(parseStepTarget(target)).toBe(stepOrder);
  });

  it("shortens long step text to one line", () => {
    expect(truncateText("Open\nthe   cart", 60)).toBe("Open the cart");
    expect(truncateText("Pay with a saved card", 10)).toBe("Pay with…");
  });
});
