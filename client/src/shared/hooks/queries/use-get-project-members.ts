"use client";

import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";

export const GET_PROJECT_MEMBERS_KEY = "GET_PROJECT_MEMBERS_KEY";

export type GetProjectMembersQueryKey = [typeof GET_PROJECT_MEMBERS_KEY, string];

type Result = Pick<
  UseQueryResult<ProjectMember[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "isFetching" | "refetch"
>;

export const useGetProjectMembers = (projectKey: string): Result => {
  const { data, error, isPending, isError, isFetching, refetch } = useAppQuery<
    ProjectMember[],
    GetProjectMembersQueryKey
  >({
    queryKey: [GET_PROJECT_MEMBERS_KEY, projectKey],
    queryFn: () => {
      return unwrapResponse(
        apiClient.GET("/api/projects/{project_key}/members", {
          params: { path: { project_key: projectKey } },
        }),
      );
    },
  });

  return { data, error, isPending, isError, isFetching, refetch };
};
