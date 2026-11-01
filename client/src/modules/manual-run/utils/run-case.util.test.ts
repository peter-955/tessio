import { describe, expect, it } from "vitest";
import {
  FIRST_CASE_ID,
  SECOND_CASE_ID,
  THIRD_CASE_ID,
  buildRecordedResult,
  buildRunCase,
} from "../test/utils/run.fixture";
import { findNextUnrecordedCase } from "./run-case.util";

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
