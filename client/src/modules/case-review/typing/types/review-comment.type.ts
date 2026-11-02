import type { components } from "@/lib/api/openapi.type";

export type ReviewComment = components["schemas"]["ReviewCommentResponse"];

export type CreateReviewCommentRequest = components["schemas"]["CreateReviewCommentRequest"];

export interface ReviewCommentGroups {
  open: ReviewComment[];
  resolved: ReviewComment[];
}
