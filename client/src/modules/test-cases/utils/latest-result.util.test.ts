import { describe, expect, it } from "vitest";
import { buildCaseLatestResult } from "../test/utils/case-latest-result-fixture.util";
import { mapLatestResultByCaseId } from "./latest-result.util";

describe("mapLatestResultByCaseId", () => {
  it("indexes the latest result by case id and keeps cases without a result", () => {
    const withResult = buildCaseLatestResult();
    const withoutResult = buildCaseLatestResult({
      caseId: "e1000000-0000-4000-8000-000000000002",
      code: "TC-2",
      latestResult: null,
    });

    const latestResultByCaseId = mapLatestResultByCaseId([withResult, withoutResult]);

    expect(latestResultByCaseId.get(withResult.caseId)).toBe(withResult.latestResult);
    expect(latestResultByCaseId.get(withoutResult.caseId)).toBeNull();
    expect(latestResultByCaseId.has("missing")).toBe(false);
  });
});
