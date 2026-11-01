"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import { keepPreviousData, skipToken, type UseQueryResult } from "@tanstack/react-query";
import type { MemberCandidate } from "../../typing/types/member-candidate.type";

export const GET_MEMBER_CANDIDATES_KEY = "GET_MEMBER_CANDIDATES_KEY";

export type GetMemberCandidatesQueryKey = [typeof GET_MEMBER_CANDIDATES_KEY, string, string];

type Result = Pick<
  UseQueryResult<MemberCandidate[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetMemberCandidates = (
  projectKey: string,
  query: string,
  isEnabled: boolean,
): Result => {
  const trimmedQuery = query.trim();
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    MemberCandidate[],
    GetMemberCandidatesQueryKey
  >({
    queryKey: [GET_MEMBER_CANDIDATES_KEY, projectKey, trimmedQuery],
    queryFn: isEnabled
      ? () => {
          return unwrapResponse(
            apiClient.GET("/api/projects/{project_key}/members/candidates", {
              params: {
                path: { project_key: projectKey },
                query: trimmedQuery === "" ? {} : { query: trimmedQuery },
              },
            }),
          );
        }
      : skipToken,
    enabled: isEnabled,
    placeholderData: keepPreviousData,
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
