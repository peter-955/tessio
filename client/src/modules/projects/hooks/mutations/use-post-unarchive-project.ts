"use client";

import type { Project } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { GET_PROJECTS_KEY } from "@/shared/hooks/queries/use-get-projects";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";

type Result = Pick<UseMutationResult<Project, ApiError, string>, "mutate" | "isPending" | "reset">;

export const usePostUnarchiveProject = (): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, reset } = useAppMutation<Project, string>({
    mutationFn: (projectKey) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/unarchive", {
          params: { path: { project_key: projectKey } },
        }),
      );
    },
    onSuccess: (project, projectKey) => {
      queryClient.setQueryData([GET_PROJECT_KEY, projectKey], project);
      void queryClient.invalidateQueries({ queryKey: [GET_PROJECTS_KEY] });
    },
  });

  return { mutate, isPending, reset };
};
