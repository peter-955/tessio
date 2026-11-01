import type { DSStepEditorStep } from "./step-editor.type";

export const createStep = (action = "", expected = ""): DSStepEditorStep => {
  return { id: crypto.randomUUID(), action, expected };
};

export const moveStep = (
  steps: readonly DSStepEditorStep[],
  index: number,
  offset: number,
): DSStepEditorStep[] => {
  const targetIndex = index + offset;
  const movingStep = steps[index];

  if (movingStep === undefined || targetIndex < 0 || targetIndex >= steps.length) {
    return [...steps];
  }

  const remainingSteps = steps.filter((_, stepIndex) => {
    return stepIndex !== index;
  });

  return [
    ...remainingSteps.slice(0, targetIndex),
    movingStep,
    ...remainingSteps.slice(targetIndex),
  ];
};

export const removeStep = (
  steps: readonly DSStepEditorStep[],
  stepId: string,
): DSStepEditorStep[] => {
  return steps.filter((step) => {
    return step.id !== stepId;
  });
};
