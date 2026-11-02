import type { TestCaseVersion, TestStep } from "../typing/types/test-case.type";

export const labelSharedSteps = (
  steps: readonly TestStep[],
  formatSharedStep: (sharedStepKey: string) => string,
): TestStep[] => {
  return steps.map((step) => {
    return step.sharedStepKey === null
      ? step
      : { ...step, action: formatSharedStep(step.sharedStepKey), expected: null };
  });
};

export const labelVersionSharedSteps = (
  version: TestCaseVersion,
  formatSharedStep: (sharedStepKey: string) => string,
): TestCaseVersion => {
  return { ...version, steps: labelSharedSteps(version.steps, formatSharedStep) };
};
