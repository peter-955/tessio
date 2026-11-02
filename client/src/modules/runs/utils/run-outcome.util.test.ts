import { describe, expect, it } from "vitest";
import { resolveCaseOutcome, resolveStepOutcome } from "./run-outcome.util";

const RESULT = {
  id: "d1000000-0000-4000-8000-000000000001",
  status: "failed" as const,
  durationMs: 1200,
  suspectedCause: null,
  causeReason: null,
  recordedAt: "2026-10-20T10:00:00Z",
  iteration: 0,
};

describe("resolveCaseOutcome", () => {
  it("returns the recorded status", () => {
    expect(resolveCaseOutcome(RESULT, "running")).toBe("failed");
    expect(resolveCaseOutcome(RESULT, "passed")).toBe("failed");
  });

  it("is pending while the run is running and not reported once it ends", () => {
    expect(resolveCaseOutcome(null, "running")).toBe("pending");
    expect(resolveCaseOutcome(null, "failed")).toBe("not_reported");
    expect(resolveCaseOutcome(null, "aborted")).toBe("not_reported");
  });
});

describe("resolveStepOutcome", () => {
  it("returns the step status when there is one", () => {
    expect(resolveStepOutcome("skipped", "failed")).toBe("skipped");
  });

  it("follows a pending case and otherwise is not reported", () => {
    expect(resolveStepOutcome(null, "pending")).toBe("pending");
    expect(resolveStepOutcome(null, "not_reported")).toBe("not_reported");
    expect(resolveStepOutcome(null, "failed")).toBe("not_reported");
  });
});
