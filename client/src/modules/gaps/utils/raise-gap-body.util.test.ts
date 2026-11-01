import { describe, expect, it } from "vitest";
import type { RaiseGapInput } from "../typing/types/raise-gap-values.type";
import { buildRaiseGapBody } from "./raise-gap-body.util";

const VALUES: RaiseGapInput = {
  type: "unclear_goal",
  severity: "high",
  targetType: "story",
  targetRef: "AC-2",
  dataScope: "project",
  question: "  Which cards are accepted?  ",
  assigneeId: null,
};

describe("buildRaiseGapBody", () => {
  it("trims the question and leaves out the target ref and data scope for a story gap", () => {
    expect(buildRaiseGapBody(VALUES)).toEqual({
      type: "unclear_goal",
      severity: "high",
      targetType: "story",
      question: "Which cards are accepted?",
      assigneeId: null,
    });
  });

  it("sends the target ref for a criterion or a test case", () => {
    expect(buildRaiseGapBody({ ...VALUES, targetType: "criterion" })).toMatchObject({
      targetType: "criterion",
      targetRef: "AC-2",
    });
    expect(
      buildRaiseGapBody({ ...VALUES, targetType: "test_case", targetRef: "TC-4" }),
    ).toMatchObject({ targetType: "test_case", targetRef: "TC-4" });
  });

  it("sends the data scope only for missing test data and keeps the chosen assignee", () => {
    const body = buildRaiseGapBody({
      ...VALUES,
      type: "missing_test_data",
      assigneeId: "a1000000-0000-4000-8000-000000000003",
    });

    expect(body).toEqual({
      type: "missing_test_data",
      severity: "high",
      targetType: "story",
      question: "Which cards are accepted?",
      dataScope: "project",
      assigneeId: "a1000000-0000-4000-8000-000000000003",
    });
  });
});
