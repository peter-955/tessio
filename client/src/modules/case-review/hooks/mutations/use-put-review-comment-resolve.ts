"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ReviewComment } from "../../typing/types/review-comment.type";
import { GET_REVIEW_COMMENTS_KEY } from "../queries/use-get-review-comments";

type Result = Pick<
  UseMutationResult<ReviewComment, ApiError, string>,
  "mutate" | "isPending" | "variables"
>;

export const usePutReviewCommentResolve = (projectKey: string, caseCode: string): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, variables } = useAppMutation<ReviewComment, string>({
    mutationFn: (commentId) => {
      return unwrapResponse(
        apiClient.PUT(
          "/api/projects/{project_key}/test-cases/{case_code}/review-comments/{comment_id}/resolve",
          {
            params: {
              path: { project_key: projectKey, case_code: caseCode, comment_id: commentId },
            },
          },
        ),
      );
    },
    onSettled: () => {
      void queryClient.invalidateQueries({
        queryKey: [GET_REVIEW_COMMENTS_KEY, projectKey, caseCode],
      });
    },
  });

  return { mutate, isPending, variables };
};
