import type { DSStepEditorStep } from "@/components/design-system";
import {
  MAX_SHARED_STEP_ACTIONS,
  MAX_SHARED_STEP_TEXT_LENGTH,
  MAX_SHARED_STEP_TITLE_LENGTH,
  SHARED_STEP_KEY_PATTERN,
} from "../typing/constants/shared-step.constant";
import type {
  SharedStepFormErrorKey,
  SharedStepFormErrors,
} from "../typing/types/shared-step-form-errors.type";
import type { SharedStepFormValues } from "../typing/types/shared-step-form-values.type";
import type {
  CreateSharedStepRequest,
  SharedStep,
  SharedStepAction,
  SharedStepActionRequest,
  UpdateSharedStepRequest,
} from "../typing/types/shared-step.type";

const createEditorStep = (action = "", expected = ""): DSStepEditorStep => {
  return { id: crypto.randomUUID(), action, expected, sharedStepKey: null };
};

const normalizeOptionalText = (value: string): string | null => {
  const trimmedValue = value.trim();

  return trimmedValue === "" ? null : trimmedValue;
};

const findTextError = (value: string, maxLength: number): SharedStepFormErrorKey | undefined => {
  if (value.trim() === "") {
    return "required";
  }

  return value.trim().length > maxLength ? "tooLong" : undefined;
};

export const normalizeSharedStepKey = (key: string): string => {
  return key.trim().toLowerCase();
};

export const sortSharedStepActions = (actions: readonly SharedStepAction[]): SharedStepAction[] => {
  return [...actions].sort((first, second) => first.order - second.order);
};

export const createEmptySharedStepFormValues = (): SharedStepFormValues => {
  return { key: "", title: "", steps: [createEditorStep()] };
};

export const buildSharedStepFormValues = (sharedStep: SharedStep): SharedStepFormValues => {
  return {
    key: sharedStep.key,
    title: sharedStep.title,
    steps: sortSharedStepActions(sharedStep.currentVersion.steps).map((step) => {
      return createEditorStep(step.action, step.expected ?? "");
    }),
  };
};

export const validateSharedStepForm = (values: SharedStepFormValues): SharedStepFormErrors => {
  const stepActions: Record<string, SharedStepFormErrorKey> = {};
  for (const step of values.steps) {
    const error = findTextError(step.action, MAX_SHARED_STEP_TEXT_LENGTH);
    if (error !== undefined) {
      stepActions[step.id] = error;
    }
  }

  const key = normalizeSharedStepKey(values.key);
  const keyError =
    key === "" ? "required" : SHARED_STEP_KEY_PATTERN.test(key) ? undefined : "invalidKey";
  const stepsError =
    values.steps.length === 0
      ? "required"
      : values.steps.length > MAX_SHARED_STEP_ACTIONS
        ? "tooMany"
        : undefined;

  return {
    key: keyError,
    title: findTextError(values.title, MAX_SHARED_STEP_TITLE_LENGTH),
    steps: stepsError,
    stepActions,
  };
};

export const checkHasSharedStepFormErrors = (errors: SharedStepFormErrors): boolean => {
  const { stepActions, ...fieldErrors } = errors;

  return (
    Object.values(fieldErrors).some((error) => error !== undefined) ||
    Object.keys(stepActions).length > 0
  );
};

const buildActionRequests = (values: SharedStepFormValues): SharedStepActionRequest[] => {
  return values.steps.map((step) => {
    return { action: step.action.trim(), expected: normalizeOptionalText(step.expected) };
  });
};

const checkAreActionsEqual = (
  requests: readonly SharedStepActionRequest[],
  actions: readonly SharedStepAction[],
): boolean => {
  const sortedActions = sortSharedStepActions(actions);

  return (
    requests.length === sortedActions.length &&
    requests.every((request, index) => {
      const action = sortedActions[index];

      return (
        action !== undefined &&
        request.action === action.action &&
        (request.expected ?? null) === (action.expected ?? null)
      );
    })
  );
};

export const buildCreateSharedStepRequest = (
  values: SharedStepFormValues,
): CreateSharedStepRequest => {
  return {
    key: normalizeSharedStepKey(values.key),
    title: values.title.trim(),
    steps: buildActionRequests(values),
  };
};

export const buildUpdateSharedStepRequest = (
  values: SharedStepFormValues,
  sharedStep: SharedStep,
): UpdateSharedStepRequest => {
  const title = values.title.trim();
  const steps = buildActionRequests(values);

  return {
    baseVersionNumber: sharedStep.currentVersion.number,
    ...(title === sharedStep.title ? {} : { title }),
    ...(checkAreActionsEqual(steps, sharedStep.currentVersion.steps) ? {} : { steps }),
  };
};

export const checkHasSharedStepChanges = (request: UpdateSharedStepRequest): boolean => {
  return request.title !== undefined || request.steps !== undefined;
};

export const listInsertableSharedSteps = (sharedSteps: readonly SharedStep[]): SharedStep[] => {
  return sharedSteps.filter((sharedStep) => !sharedStep.isArchived);
};
