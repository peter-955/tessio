import { describe, expect, it } from "vitest";
import { computeRunDuration } from "./run-duration.util";

describe("computeRunDuration", () => {
  it("returns the milliseconds between start and finish", () => {
    expect(computeRunDuration("2026-10-20T10:00:00Z", "2026-10-20T10:02:05Z")).toBe(125000);
  });

  it("is null while the run has not finished", () => {
    expect(computeRunDuration("2026-10-20T10:00:00Z", null)).toBeNull();
  });

  it("never goes below zero", () => {
    expect(computeRunDuration("2026-10-20T10:00:05Z", "2026-10-20T10:00:00Z")).toBe(0);
  });
});
