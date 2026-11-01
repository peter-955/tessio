import { describe, expect, it } from "vitest";
import { buildFailure, buildFailureRun } from "../test/utils/failure-fixture.util";
import { findRunStep } from "./failed-step.util";

describe("findRunStep", () => {
  it("finds the step of the failing case result by its order", () => {
    const step = findRunStep(buildFailureRun(), buildFailure(), 2);

    expect(step).toMatchObject({ order: 2, action: "Click Pay with a valid card" });
  });

  it("returns null for another case result, another case or a missing step", () => {
    const run = buildFailureRun();

    expect(
      findRunStep(
        run,
        buildFailure({ latestCaseResultId: "d1000000-0000-4000-8000-0000000000ff" }),
        2,
      ),
    ).toBeNull();
    expect(
      findRunStep(run, buildFailure({ testCaseId: "e1000000-0000-4000-8000-0000000000ff" }), 2),
    ).toBeNull();
    expect(findRunStep(run, buildFailure(), 9)).toBeNull();
  });
});
