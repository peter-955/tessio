import {
  TEST_CASE_PRIMARY_STATUS,
  TEST_CASE_STATUS_ACTION_ORDER,
  TEST_CASE_STATUS_TRANSITIONS,
} from "../typing/constants/test-case.constant";
import type {
  TestCaseStatusAction,
  TestCaseStatusActionLabel,
  TestCaseStatusActions,
} from "../typing/types/test-case-status-action.type";
import type { TestCaseStatus } from "../typing/types/test-case.type";

export const checkCanChangeTestCaseStatus = (from: TestCaseStatus, to: TestCaseStatus): boolean => {
  return TEST_CASE_STATUS_TRANSITIONS[from].includes(to);
};

export const resolveStatusActionLabel = (
  from: TestCaseStatus,
  to: TestCaseStatus,
): TestCaseStatusActionLabel => {
  switch (to) {
    case "in_review":
      return from === "draft" ? "submitForReview" : "backToReview";
    case "ready":
      return "markReady";
    case "draft":
      return from === "deprecated" ? "restore" : "backToDraft";
    case "deprecated":
      return "deprecate";
  }
};

const buildStatusAction = (from: TestCaseStatus, to: TestCaseStatus): TestCaseStatusAction => {
  return { status: to, label: resolveStatusActionLabel(from, to) };
};

export const buildTestCaseStatusActions = (status: TestCaseStatus): TestCaseStatusActions => {
  const primaryStatus = TEST_CASE_PRIMARY_STATUS[status];
  const secondaryStatuses = TEST_CASE_STATUS_ACTION_ORDER.filter((nextStatus) => {
    return nextStatus !== primaryStatus && checkCanChangeTestCaseStatus(status, nextStatus);
  });

  return {
    primary:
      primaryStatus !== null && checkCanChangeTestCaseStatus(status, primaryStatus)
        ? buildStatusAction(status, primaryStatus)
        : null,
    secondary: secondaryStatuses.map((nextStatus) => buildStatusAction(status, nextStatus)),
  };
};
