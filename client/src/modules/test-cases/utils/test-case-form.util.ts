import {
  DEFAULT_TEST_CASE_PRIORITY,
  MAX_CRITERION_LINKS,
  MAX_STEPS,
  MAX_TEXT_LENGTH,
  MAX_TITLE_LENGTH,
} from "../typing/constants/test-case.constant";
import type {
  TestCaseFormErrorKey,
  TestCaseFormErrors,
} from "../typing/types/test-case-form-errors.type";
import type { TestCaseFormValues } from "../typing/types/test-case-form-values.type";
import type {
  CreateTestCaseRequest,
  TestCaseVersion,
  TestStepRequest,
  UpdateTestCaseRequest,
} from "../typing/types/test-case.type";
import { createFormStep } from "./form-step.util";

const UPDATE_REQUEST_BASE_FIELD_COUNT = 1;

const CLEARED_TEXT = "";

const normalizeOptionalText = (value: string): string | null => {
  const trimmedValue = value.trim();

  return trimmedValue === "" ? null : trimmedValue;
};

const findTextError = (value: string, maxLength: number): TestCaseFormErrorKey | undefined => {
  return value.trim().length > maxLength ? "tooLong" : undefined;
};

const buildStepRequests = (values: TestCaseFormValues): TestStepRequest[] => {
  return values.steps.map((step) => {
    return { action: step.action.trim(), expected: normalizeOptionalText(step.expected) };
  });
};

const checkAreStepsEqual = (
  steps: readonly TestStepRequest[],
  version: TestCaseVersion,
): boolean => {
  const versionSteps = [...version.steps].sort((first, second) => first.order - second.order);

  return (
    steps.length === versionSteps.length &&
    steps.every((step, index) => {
      const versionStep = versionSteps[index];

      return (
        versionStep !== undefined &&
        step.action === versionStep.action &&
        (step.expected ?? null) === (versionStep.expected ?? null)
      );
    })
  );
};

const checkAreIdsEqual = (first: readonly string[], second: readonly string[]): boolean => {
  const sortedFirst = [...first].sort();
  const sortedSecond = [...second].sort();

  return (
    sortedFirst.length === sortedSecond.length &&
    sortedFirst.every((id, index) => id === sortedSecond[index])
  );
};

export const createEmptyTestCaseFormValues = (storyKey: string | null): TestCaseFormValues => {
  return {
    storyKey,
    title: "",
    priority: DEFAULT_TEST_CASE_PRIORITY,
    businessValue: "",
    preconditions: "",
    criterionIds: [],
    steps: [createFormStep()],
  };
};

export const buildTestCaseFormValues = (
  version: TestCaseVersion,
  storyKey: string,
): TestCaseFormValues => {
  return {
    storyKey,
    title: version.title,
    priority: version.priority,
    businessValue: version.businessValue ?? "",
    preconditions: version.preconditions ?? "",
    criterionIds: [...version.criterionIds],
    steps: [...version.steps]
      .sort((first, second) => first.order - second.order)
      .map((step) => createFormStep(step.action, step.expected ?? "")),
  };
};

export const validateTestCaseForm = (values: TestCaseFormValues): TestCaseFormErrors => {
  const stepActions: Record<string, TestCaseFormErrorKey> = {};

  for (const step of values.steps) {
    const actionError =
      step.action.trim() === "" ? "required" : findTextError(step.action, MAX_TEXT_LENGTH);
    if (actionError !== undefined) {
      stepActions[step.id] = actionError;
    }
  }

  const titleError =
    values.title.trim() === "" ? "required" : findTextError(values.title, MAX_TITLE_LENGTH);
  const errors: TestCaseFormErrors = {
    storyKey: values.storyKey === null ? "required" : undefined,
    title: titleError,
    businessValue: findTextError(values.businessValue, MAX_TEXT_LENGTH),
    preconditions: findTextError(values.preconditions, MAX_TEXT_LENGTH),
    criterionIds: values.criterionIds.length > MAX_CRITERION_LINKS ? "tooMany" : undefined,
    steps: values.steps.length > MAX_STEPS ? "tooMany" : undefined,
    stepActions,
  };

  return errors;
};

export const checkHasTestCaseFormErrors = (errors: TestCaseFormErrors): boolean => {
  const { stepActions, ...fieldErrors } = errors;

  return (
    Object.values(fieldErrors).some((error) => error !== undefined) ||
    Object.keys(stepActions).length > 0
  );
};

export const buildCreateTestCaseRequest = (
  values: TestCaseFormValues,
  storyKey: string,
): CreateTestCaseRequest => {
  return {
    storyKey,
    title: values.title.trim(),
    priority: values.priority,
    businessValue: normalizeOptionalText(values.businessValue),
    preconditions: normalizeOptionalText(values.preconditions),
    steps: buildStepRequests(values),
    criterionIds: [...values.criterionIds],
  };
};

export const buildUpdateTestCaseRequest = (
  values: TestCaseFormValues,
  baseVersion: TestCaseVersion,
): UpdateTestCaseRequest => {
  const title = values.title.trim();
  const businessValue = normalizeOptionalText(values.businessValue);
  const preconditions = normalizeOptionalText(values.preconditions);
  const steps = buildStepRequests(values);

  return {
    baseVersionNumber: baseVersion.number,
    ...(title === baseVersion.title ? {} : { title }),
    ...(values.priority === baseVersion.priority ? {} : { priority: values.priority }),
    ...(businessValue === (baseVersion.businessValue ?? null)
      ? {}
      : { businessValue: businessValue ?? CLEARED_TEXT }),
    ...(preconditions === (baseVersion.preconditions ?? null)
      ? {}
      : { preconditions: preconditions ?? CLEARED_TEXT }),
    ...(checkAreStepsEqual(steps, baseVersion) ? {} : { steps }),
    ...(checkAreIdsEqual(values.criterionIds, baseVersion.criterionIds)
      ? {}
      : { criterionIds: [...values.criterionIds] }),
  };
};

export const checkHasTestCaseChanges = (request: UpdateTestCaseRequest): boolean => {
  return Object.keys(request).length > UPDATE_REQUEST_BASE_FIELD_COUNT;
};
