import { ERROR_RESULT_STATUSES } from "../typing/constants/result-status.constant";
import type { CaseDraft } from "../typing/types/case-draft.type";
import type {
  ManualCaseResultRequest,
  ManualRunStep,
  ManualStepResultInput,
  ResultStatus,
} from "../typing/types/manual-run.type";
import type { StepDraft } from "../typing/types/step-draft.type";
import { readStepDraft } from "./step-draft.util";

const buildStepError = (status: ResultStatus, error: string): string | null => {
  const trimmedError = error.trim();

  return ERROR_RESULT_STATUSES.includes(status) && trimmedError !== "" ? trimmedError : null;
};

const buildStepInput = (order: number, stepDraft: StepDraft): ManualStepResultInput | null => {
  if (stepDraft.status === null) {
    return null;
  }

  return {
    order,
    status: stepDraft.status,
    actualResult: stepDraft.actualResult.trim(),
    error: buildStepError(stepDraft.status, stepDraft.error),
    evidenceFileId: stepDraft.evidenceFile?.id ?? null,
  };
};

export const createEmptyCaseDraft = (): CaseDraft => {
  return { steps: {}, statusOverride: null };
};

export const checkIsCaseDraftUploading = (draft: CaseDraft): boolean => {
  return Object.values(draft.steps).some((stepDraft) => {
    return stepDraft.isUploading;
  });
};

export const listDraftStatuses = (
  draft: CaseDraft,
  steps: readonly ManualRunStep[],
): (ResultStatus | null)[] => {
  return steps.map((step) => {
    return readStepDraft(draft, step.order).status;
  });
};

export const buildCaseResultRequest = (
  draft: CaseDraft,
  steps: readonly ManualRunStep[],
): ManualCaseResultRequest => {
  const stepInputs = steps.flatMap((step): ManualStepResultInput[] => {
    const stepInput = buildStepInput(step.order, readStepDraft(draft, step.order));

    return stepInput === null ? [] : [stepInput];
  });

  return { status: draft.statusOverride, durationMs: null, steps: stepInputs };
};
