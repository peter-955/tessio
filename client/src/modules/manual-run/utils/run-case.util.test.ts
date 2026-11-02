import { describe, expect, it } from "vitest";
import {
  FIRST_CASE_ID,
  SECOND_CASE_ID,
  THIRD_CASE_ID,
  buildRecordedResult,
  buildRunCase,
} from "../test/utils/run.fixture";
import {
  checkIsCaseRecorded,
  countRecordedCases,
  findFirstUnrecordedIteration,
  findNextUnrecordedCase,
  findNextUnrecordedIteration,
} from "./run-case.util";

const FIRST_CASE = buildRunCase({ testCaseId: FIRST_CASE_ID, position: 1 });
const SECOND_CASE = buildRunCase({ testCaseId: SECOND_CASE_ID, position: 2 });
const THIRD_CASE = buildRunCase({ testCaseId: THIRD_CASE_ID, position: 3 });

describe("findNextUnrecordedCase", () => {
  it("picks the next unrecorded case by position", () => {
    expect(
      findNextUnrecordedCase([THIRD_CASE, SECOND_CASE, FIRST_CASE], FIRST_CASE_ID)?.testCaseId,
    ).toBe(SECOND_CASE_ID);
  });

  it("wraps around to earlier unrecorded cases", () => {
    const recordedThird = { ...THIRD_CASE, result: buildRecordedResult("passed") };

    expect(
      findNextUnrecordedCase([FIRST_CASE, SECOND_CASE, recordedThird], SECOND_CASE_ID)?.testCaseId,
    ).toBe(FIRST_CASE_ID);
  });

  it("returns null when every other case is recorded", () => {
    const recordedSecond = { ...SECOND_CASE, result: buildRecordedResult("failed") };

    expect(findNextUnrecordedCase([FIRST_CASE, recordedSecond], FIRST_CASE_ID)).toBeNull();
  });
});

describe("data-driven cases", () => {
  const buildIterations = (recorded: readonly number[]) => {
    return [0, 1, 2].map((iteration) => {
      return {
        iteration,
        values: { email: `user${iteration}@shop.test` },
        result: recorded.includes(iteration)
          ? { ...buildRecordedResult("passed"), iteration }
          : null,
        steps: [],
      };
    });
  };

  it("is recorded only when every iteration has a result", () => {
    const partly = buildRunCase({
      result: buildRecordedResult("passed"),
      parameters: ["email"],
      iterations: buildIterations([0, 2]),
    });
    const fully = { ...partly, iterations: buildIterations([0, 1, 2]) };

    expect(checkIsCaseRecorded(partly)).toBe(false);
    expect(checkIsCaseRecorded(fully)).toBe(true);
    expect(countRecordedCases([partly, fully])).toBe(1);
    expect(findNextUnrecordedCase([FIRST_CASE, partly], FIRST_CASE_ID)?.testCaseId).toBe(
      partly.testCaseId,
    );
  });

  it("finds the next iteration to record after the current one, then wraps", () => {
    const runCase = buildRunCase({ parameters: ["email"], iterations: buildIterations([1]) });

    expect(findFirstUnrecordedIteration(runCase)).toBe(0);
    expect(findNextUnrecordedIteration(runCase, 0)).toBe(2);
    expect(findNextUnrecordedIteration(runCase, 2)).toBe(0);
    expect(
      findNextUnrecordedIteration({ ...runCase, iterations: buildIterations([0, 1]) }, 2),
    ).toBeNull();
  });
});
