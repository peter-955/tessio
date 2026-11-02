"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type {
  CreateReviewCommentRequest,
  ReviewComment,
} from "../../typing/types/review-comment.type";
import { GET_REVIEW_COMMENTS_KEY } from "../queries/use-get-review-comments";

type Result = Pick<
  UseMutationResult<ReviewComment, ApiError, CreateReviewCommentRequest>,
  "mutate" | "isPending"
>;

export const usePostReviewComment = (projectKey: string, caseCode: string): Result => {
  const { t } = useTranslation("caseReview");
  const queryClient = useQueryClient();
  const { mutate, isPending } = useAppMutation<ReviewComment, CreateReviewCommentRequest>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-cases/{case_code}/review-comments", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          body,
        }),
      );
    },
    apiErrors: {
      INVALID_REQUEST: t("comments.errors.stepMissing"),
      CONFLICT: t("comments.errors.deprecated"),
    },
    onSettled: () => {
      void queryClient.invalidateQueries({
        queryKey: [GET_REVIEW_COMMENTS_KEY, projectKey, caseCode],
      });
    },
  });

  return { mutate, isPending };
};
