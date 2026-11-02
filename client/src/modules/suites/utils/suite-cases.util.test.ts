import { describe, expect, it } from "vitest";
import { SUITE_CASES, buildSuiteCase } from "../test/utils/suite.fixture";
import {
  appendCaseIds,
  findSuiteCaseSkipReason,
  listRunnableSuiteCases,
  listSkippedSuiteCases,
  listSuiteCaseIds,
  moveCaseId,
  orderSuiteCases,
  removeCaseId,
} from "./suite-cases.util";

describe("moveCaseId", () => {
  it("moves a case up, down, to the top and to the bottom", () => {
    expect(moveCaseId(["a", "b", "c"], 2, 0)).toEqual(["c", "a", "b"]);
    expect(moveCaseId(["a", "b", "c"], 0, 2)).toEqual(["b", "c", "a"]);
    expect(moveCaseId(["a", "b", "c"], 1, 0)).toEqual(["b", "a", "c"]);
  });

  it("keeps the order for a move out of range", () => {
    expect(moveCaseId(["a", "b"], 0, -1)).toEqual(["a", "b"]);
    expect(moveCaseId(["a", "b"], 5, 0)).toEqual(["a", "b"]);
  });
});

describe("removeCaseId and appendCaseIds", () => {
  it("removes one case", () => {
    expect(removeCaseId(["a", "b", "c"], "b")).toEqual(["a", "c"]);
  });

  it("appends new cases once, after the current ones", () => {
    expect(appendCaseIds(["a", "b"], ["c", "a", "c", "d"])).toEqual(["a", "b", "c", "d"]);
  });
});

describe("orderSuiteCases", () => {
  it("follows the given ids and drops unknown ones", () => {
    const ids = listSuiteCaseIds(SUITE_CASES);

    expect(
      orderSuiteCases(SUITE_CASES, [ids[2], "missing", ids[0]]).map((suiteCase) => {
        return suiteCase.code;
      }),
    ).toEqual(["TC-3", "TC-1"]);
  });
});

describe("skip reasons", () => {
  it("splits runnable cases from the ones a run skips", () => {
    expect(listRunnableSuiteCases(SUITE_CASES)).toHaveLength(2);
    expect(listSkippedSuiteCases(SUITE_CASES).map((suiteCase) => suiteCase.code)).toEqual(["TC-3"]);
  });

  it("names why a case is skipped", () => {
    expect(findSuiteCaseSkipReason(buildSuiteCase())).toBeNull();
    expect(findSuiteCaseSkipReason(buildSuiteCase({ status: "in_review" }))).toBe("not_ready");
    expect(findSuiteCaseSkipReason(buildSuiteCase({ isNeedingReview: true }))).toBe("needs_review");
  });
});
