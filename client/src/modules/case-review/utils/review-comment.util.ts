import type { Project } from "@/components/project-context/typing/types/project.type";
import type { TestCaseStatusActions } from "@/modules/test-cases/typing/types/test-case-status-action.type";
import type { TestCaseDetail } from "@/modules/test-cases/typing/types/test-case.type";
import { WHOLE_CASE_TARGET } from "../typing/constants/review-comment.constant";
import type { ReviewComment, ReviewCommentGroups } from "../typing/types/review-comment.type";

export const groupReviewComments = (comments: readonly ReviewComment[]): ReviewCommentGroups => {
  return {
    open: comments.filter((comment) => !comment.isResolved),
    resolved: comments.filter((comment) => comment.isResolved),
  };
};

export const countOpenReviewComments = (comments: readonly ReviewComment[] | undefined): number => {
  return (comments ?? []).filter((comment) => !comment.isResolved).length;
};

export const checkIsAuthorReviewBlocked = (
  project: Pick<Project, "requireSeparateReviewer">,
  detail: Pick<TestCaseDetail, "currentVersion">,
  userId: string | null,
): boolean => {
  return (
    project.requireSeparateReviewer && userId !== null && detail.currentVersion.createdBy === userId
  );
};

export const removeReadyAction = (actions: TestCaseStatusActions): TestCaseStatusActions => {
  return {
    primary: actions.primary?.status === "ready" ? null : actions.primary,
    secondary: actions.secondary.filter((action) => action.status !== "ready"),
  };
};

export const parseStepTarget = (target: string): number | null => {
  if (target === WHOLE_CASE_TARGET) {
    return null;
  }

  const stepOrder = Number(target);

  return Number.isInteger(stepOrder) && stepOrder > 0 ? stepOrder : null;
};

export const truncateText = (text: string, maxLength: number): string => {
  const singleLine = text.replace(/\s+/g, " ").trim();

  return singleLine.length <= maxLength
    ? singleLine
    : `${singleLine.slice(0, maxLength - 1).trimEnd()}…`;
};
