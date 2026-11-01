import type { DSStepEditorStep } from "@/components/design-system";

export const createFormStep = (action = "", expected = ""): DSStepEditorStep => {
  return { id: crypto.randomUUID(), action, expected };
};
