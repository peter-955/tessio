import { describe, expect, it } from "vitest";
import { suggestCaseStatus } from "./suggest-case-status.util";

describe("suggestCaseStatus", () => {
  it("suggests failed whenever a step failed", () => {
    expect(suggestCaseStatus(["passed", "blocked", "failed", "skipped", null])).toBe("failed");
  });

  it("suggests blocked over passed and skipped", () => {
    expect(suggestCaseStatus(["passed", "blocked", "skipped"])).toBe("blocked");
  });

  it("suggests passed over skipped and unreported steps", () => {
    expect(suggestCaseStatus(["skipped", "passed", null])).toBe("passed");
  });

  it("suggests skipped when only skipped steps are reported", () => {
    expect(suggestCaseStatus(["skipped", null])).toBe("skipped");
  });

  it("suggests skipped when no step is reported", () => {
    expect(suggestCaseStatus([null, null])).toBe("skipped");
    expect(suggestCaseStatus([])).toBe("skipped");
  });
});
