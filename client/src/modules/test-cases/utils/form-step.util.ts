import type { DSStepEditorStep } from "@/components/design-system";

export const createFormStep = (
  action = "",
  expected = "",
  sharedStepKey: string | null = null,
): DSStepEditorStep => {
  return { id: crypto.randomUUID(), action, expected, sharedStepKey };
};

export const checkIsSharedFormStep = (step: DSStepEditorStep): boolean => {
  return typeof step.sharedStepKey === "string" && step.sharedStepKey !== "";
};
