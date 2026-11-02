import { buildTestCaseVersion } from "@/modules/test-cases/test/utils/test-case-fixture.util";
import type { TestStep } from "@/modules/test-cases/typing/types/test-case.type";
import { describe, expect, it } from "vitest";
import type { CompareStepSide } from "../typing/types/version-comparison.type";
import { buildStepRows, buildVersionComparison } from "./version-comparison.util";

const step = (order: number, action: string, expected: string | null = null): TestStep => {
  return { order, action, expected, sharedStepKey: null };
};

const readText = (side: CompareStepSide | null): string | null => {
  return side === null ? null : side.action.map((token) => token.value).join("");
};

describe("buildStepRows", () => {
  it("keeps identical steps as unchanged rows", () => {
    const steps = [step(1, "Open the cart"), step(2, "Pay", "Paid")];

    const rows = buildStepRows(steps, steps);

    expect(rows.map((row) => row.kind)).toEqual(["unchanged", "unchanged"]);
    expect(rows[1].left?.expected).toEqual([{ value: "Paid", kind: "unchanged" }]);
  });

  it("lines up a step inserted in the middle instead of marking every later step changed", () => {
    const rows = buildStepRows(
      [step(1, "Open the cart"), step(2, "Pay")],
      [step(1, "Open the cart"), step(2, "Pick a card"), step(3, "Pay")],
    );

    expect(rows.map((row) => row.kind)).toEqual(["unchanged", "added", "unchanged"]);
    expect(rows[1].left).toBeNull();
    expect(rows[1].right?.action).toEqual([{ value: "Pick a card", kind: "added" }]);
    expect(rows[2].left?.order).toBe(2);
    expect(rows[2].right?.order).toBe(3);
  });

  it("marks a removed step on the older side only", () => {
    const rows = buildStepRows(
      [step(1, "Open the cart"), step(2, "Log in")],
      [step(1, "Open the cart")],
    );

    expect(rows[1]).toEqual({
      kind: "removed",
      left: { order: 2, action: [{ value: "Log in", kind: "removed" }], expected: [] },
      right: null,
    });
  });

  it("pairs an edited step and highlights only the changed words on each side", () => {
    const rows = buildStepRows(
      [step(1, "Pay with a card", "The order is paid")],
      [step(1, "Pay with a saved card", "The order is paid")],
    );

    expect(rows).toHaveLength(1);
    expect(rows[0].kind).toBe("changed");
    expect(rows[0].left?.action.some((token) => token.kind === "added")).toBe(false);
    expect(rows[0].right?.action.some((token) => token.kind === "removed")).toBe(false);
    expect(rows[0].right?.action.filter((token) => token.kind === "added")).toEqual([
      { value: "saved ", kind: "added" },
    ]);
    expect(readText(rows[0].left)).toBe("Pay with a card");
    expect(readText(rows[0].right)).toBe("Pay with a saved card");
    expect(rows[0].left?.expected).toEqual([{ value: "The order is paid", kind: "unchanged" }]);
  });

  it("treats a blank and a missing expected result as the same", () => {
    const rows = buildStepRows([step(1, "Pay", null)], [step(1, "Pay", "")]);

    expect(rows.map((row) => row.kind)).toEqual(["unchanged"]);
  });

  it("sorts steps by order before comparing", () => {
    const rows = buildStepRows(
      [step(2, "Pay"), step(1, "Open the cart")],
      [step(1, "Open the cart"), step(2, "Pay")],
    );

    expect(rows.map((row) => row.kind)).toEqual(["unchanged", "unchanged"]);
    expect(readText(rows[0].left)).toBe("Open the cart");
  });

  it("returns no rows when neither version has steps", () => {
    expect(buildStepRows([], [])).toEqual([]);
  });
});

describe("buildVersionComparison", () => {
  it("counts every changed field, priority and step row", () => {
    const older = buildTestCaseVersion({ number: 1, title: "Pay by card", priority: "medium" });
    const newer = buildTestCaseVersion({
      number: 2,
      title: "Pay with a valid card",
      priority: "high",
      preconditions: "A product is in the cart",
      steps: [...older.steps, step(3, "Check the receipt")],
    });

    const comparison = buildVersionComparison(older, newer);

    expect(comparison.fields.map((row) => [row.field, row.kind])).toEqual([
      ["title", "changed"],
      ["businessValue", "unchanged"],
      ["preconditions", "changed"],
    ]);
    expect(comparison.priority).toEqual({ kind: "changed", left: "medium", right: "high" });
    expect(comparison.steps.map((row) => row.kind)).toEqual(["unchanged", "unchanged", "added"]);
    expect(comparison.changeCount).toBe(4);
  });

  it("shows an empty older field as no tokens and the new text as added", () => {
    const comparison = buildVersionComparison(
      buildTestCaseVersion({ preconditions: null }),
      buildTestCaseVersion({ preconditions: "Signed in" }),
    );
    const preconditions = comparison.fields.find((row) => row.field === "preconditions");

    expect(preconditions?.left).toEqual([]);
    expect(preconditions?.right).toEqual([{ value: "Signed in", kind: "added" }]);
  });

  it("counts a change to only the parameters and data rows", () => {
    const older = buildTestCaseVersion({ parameters: ["email"], dataRows: [{ email: "a" }] });
    const newer = buildTestCaseVersion({ parameters: ["email"], dataRows: [{ email: "b" }] });

    const comparison = buildVersionComparison(older, newer);

    expect(comparison.changeCount).toBe(1);
    expect(comparison.dataTable?.kind).toBe("changed");
    expect(comparison.dataTable?.left).toContainEqual({ value: "a", kind: "removed" });
    expect(comparison.dataTable?.right).toContainEqual({ value: "b", kind: "added" });
  });

  it("has no data table row when neither version has parameters", () => {
    const version = buildTestCaseVersion();

    expect(buildVersionComparison(version, { ...version, number: 3 }).dataTable).toBeNull();
  });

  it("reports no change for the same version", () => {
    const version = buildTestCaseVersion();

    expect(buildVersionComparison(version, version).changeCount).toBe(0);
  });
});
