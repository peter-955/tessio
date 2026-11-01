import type { TestCaseStatus } from "./test-case.type";

export type TestCaseStatusActionLabel =
  "submitForReview" | "markReady" | "backToDraft" | "backToReview" | "deprecate" | "restore";

export interface TestCaseStatusAction {
  status: TestCaseStatus;
  label: TestCaseStatusActionLabel;
}

export interface TestCaseStatusActions {
  primary: TestCaseStatusAction | null;
  secondary: TestCaseStatusAction[];
}
