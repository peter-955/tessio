import type { CaseDraft } from "../typing/types/case-draft.type";
import type { StepDraft } from "../typing/types/step-draft.type";

export const createEmptyStepDraft = (): StepDraft => {
  return { status: null, actualResult: "", error: "", evidenceFile: null, isUploading: false };
};

export const readStepDraft = (draft: CaseDraft, order: number): StepDraft => {
  return draft.steps[order] ?? createEmptyStepDraft();
};

export const updateStepDraft = (
  draft: CaseDraft,
  order: number,
  changes: Partial<StepDraft>,
): CaseDraft => {
  return {
    ...draft,
    steps: { ...draft.steps, [order]: { ...readStepDraft(draft, order), ...changes } },
  };
};
