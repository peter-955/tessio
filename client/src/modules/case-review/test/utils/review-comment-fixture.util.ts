import { QC_USER_ID } from "@/modules/test-cases/test/utils/test-case-fixture.util";
import type { ReviewComment } from "../../typing/types/review-comment.type";

export const REVIEWER_ID = "b1000000-0000-4000-8000-000000000002";

export const OPEN_COMMENT_ID = "a5000000-0000-4000-8000-000000000001";

export const RESOLVED_COMMENT_ID = "a5000000-0000-4000-8000-000000000002";

export const buildReviewComment = (overrides: Partial<ReviewComment> = {}): ReviewComment => {
  return {
    id: OPEN_COMMENT_ID,
    versionId: "a2000000-0000-4000-8000-000000000002",
    versionNumber: 2,
    stepOrder: 2,
    body: "Say which card number to use.",
    authorId: REVIEWER_ID,
    authorName: "Rita Reviewer",
    createdAt: "2026-10-22T09:00:00Z",
    isResolved: false,
    resolvedAt: null,
    resolvedBy: null,
    resolvedByName: null,
    ...overrides,
  };
};

export const buildResolvedComment = (overrides: Partial<ReviewComment> = {}): ReviewComment => {
  return buildReviewComment({
    id: RESOLVED_COMMENT_ID,
    versionNumber: 1,
    versionId: "a2000000-0000-4000-8000-000000000001",
    stepOrder: null,
    body: "Add a business value.",
    isResolved: true,
    resolvedAt: "2026-10-22T10:00:00Z",
    resolvedBy: QC_USER_ID,
    resolvedByName: "Quinn Tester",
    ...overrides,
  });
};
