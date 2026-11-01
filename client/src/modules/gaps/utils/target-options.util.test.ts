import { describe, expect, it } from "vitest";
import { buildCriterionOptions, buildTestCaseOption, truncateLabel } from "./target-options.util";

describe("target options", () => {
  it("lists only criteria that are not removed", () => {
    const options = buildCriterionOptions([
      { id: "1", code: "AC-1", position: 1, text: "Pay", removedAt: null, isRemoved: false },
      {
        id: "2",
        code: "AC-2",
        position: 2,
        text: "Old",
        removedAt: "2026-10-01T00:00:00Z",
        isRemoved: true,
      },
    ]);

    expect(options).toEqual([{ value: "AC-1", label: "AC-1 · Pay" }]);
  });

  it("truncates long labels to 80 characters", () => {
    const label = truncateLabel(`AC-1 · ${"a".repeat(100)}`);

    expect(label).toHaveLength(80);
    expect(label.endsWith("…")).toBe(true);
    expect(truncateLabel("short")).toBe("short");
    expect(buildTestCaseOption("TC-4", "Refund")).toEqual({
      value: "TC-4",
      label: "TC-4 · Refund",
    });
  });
});
