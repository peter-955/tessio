"use client";

import type { Project } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { GET_PROJECTS_KEY } from "@/shared/hooks/queries/use-get-projects";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { UpdateProjectRequest } from "../../typing/types/project-request.type";

interface Options {
  isGlobalErrorToastDisabled?: boolean;
}

type Result = Pick<
  UseMutationResult<Project, ApiError, UpdateProjectRequest>,
  "mutate" | "isPending" | "error" | "reset"
>;

export const usePatchProject = (
  projectKey: string,
  { isGlobalErrorToastDisabled = false }: Options = {},
): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, error, reset } = useAppMutation<Project, UpdateProjectRequest>({
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.PATCH("/api/projects/{project_key}", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    isGlobalErrorToastDisabled,
    onSuccess: (project) => {
      queryClient.setQueryData([GET_PROJECT_KEY, projectKey], project);
      void queryClient.invalidateQueries({ queryKey: [GET_PROJECTS_KEY] });
    },
  });

  return { mutate, isPending, error, reset };
};
