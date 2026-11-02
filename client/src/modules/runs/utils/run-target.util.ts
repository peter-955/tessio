interface TargetedRun {
  storyId: string | null;
  testSuiteId?: string | null;
}

export const checkIsUntargetedRun = (run: TargetedRun): boolean => {
  return run.storyId === null && (run.testSuiteId ?? null) === null;
};
