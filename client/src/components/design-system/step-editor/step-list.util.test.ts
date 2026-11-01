import { describe, expect, it } from "vitest";
import type { DSStepEditorStep } from "./step-editor.type";
import { createStep, moveStep, removeStep } from "./step-list.util";

const STEPS: DSStepEditorStep[] = [
  { id: "first", action: "Open", expected: "" },
  { id: "second", action: "Type", expected: "" },
  { id: "third", action: "Submit", expected: "Saved" },
];

const readIds = (steps: DSStepEditorStep[]): string[] => {
  return steps.map((step) => step.id);
};

describe("createStep", () => {
  it("creates an empty step with a unique id", () => {
    const firstStep = createStep();
    const secondStep = createStep();

    expect(firstStep).toEqual({ id: firstStep.id, action: "", expected: "" });
    expect(firstStep.id).not.toBe(secondStep.id);
  });
});

describe("moveStep", () => {
  it("moves a step up and down", () => {
    expect(readIds(moveStep(STEPS, 2, -1))).toEqual(["first", "third", "second"]);
    expect(readIds(moveStep(STEPS, 0, 1))).toEqual(["second", "first", "third"]);
  });

  it("keeps the order when the move leaves the list", () => {
    expect(readIds(moveStep(STEPS, 0, -1))).toEqual(["first", "second", "third"]);
    expect(readIds(moveStep(STEPS, 2, 1))).toEqual(["first", "second", "third"]);
  });
});

describe("removeStep", () => {
  it("removes the step with the id", () => {
    expect(readIds(removeStep(STEPS, "second"))).toEqual(["first", "third"]);
  });
});
