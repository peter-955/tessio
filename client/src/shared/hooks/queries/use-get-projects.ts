"use client";

import type { Project } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppQuery } from "@/shared/hooks/use-app-query";
import type { UseQueryResult } from "@tanstack/react-query";

export const GET_PROJECTS_KEY = "GET_PROJECTS_KEY";

export type GetProjectsQueryKey = [typeof GET_PROJECTS_KEY, boolean];

interface Options {
  isIncludingArchived?: boolean;
}

type Result = Pick<
  UseQueryResult<Project[], ApiError>,
  "data" | "error" | "isPending" | "isError" | "refetch"
>;

export const useGetProjects = ({ isIncludingArchived = false }: Options = {}): Result => {
  const { data, error, isPending, isError, refetch } = useAppQuery<Project[], GetProjectsQueryKey>({
    queryKey: [GET_PROJECTS_KEY, isIncludingArchived],
    queryFn: () => {
      return unwrapResponse(
        apiClient.GET("/api/projects", {
          params: { query: { includeArchived: isIncludingArchived } },
        }),
      );
    },
    isGlobalErrorToastDisabled: true,
  });

  return { data, error, isPending, isError, refetch };
};
