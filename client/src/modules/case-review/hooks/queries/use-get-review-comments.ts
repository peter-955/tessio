"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";
import type { ReviewComment } from "../../typing/types/review-comment.type";

export const GET_REVIEW_COMMENTS_KEY = "GET_REVIEW_COMMENTS_KEY";

export type GetReviewCommentsQueryKey = [typeof GET_REVIEW_COMMENTS_KEY, string, string];

type Result = Pick<
  UseQueryResult<ReviewComment[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetReviewComments = (projectKey: string, caseCode: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    ReviewComment[],
    GetReviewCommentsQueryKey
  >({
    queryKey: [GET_REVIEW_COMMENTS_KEY, projectKey, caseCode],
    queryFn: ({ signal }) => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/test-cases/{case_code}/review-comments", {
          params: { path: { project_key: projectKey, case_code: caseCode } },
          signal,
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
