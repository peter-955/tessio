"use client";

import type { Project } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_PROJECTS_KEY } from "@/shared/hooks/queries/use-get-projects";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { CreateProjectRequest } from "../../typing/types/project-request.type";

type Result = Pick<
  UseMutationResult<Project, ApiError, CreateProjectRequest>,
  "mutate" | "isPending" | "error" | "reset"
>;

export const usePostProject = (): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, error, reset } = useAppMutation<Project, CreateProjectRequest>({
    mutationFn: (body) => {
      return unwrapResponse(apiClient.POST("/api/projects", { body }));
    },
    isGlobalErrorToastDisabled: true,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [GET_PROJECTS_KEY] });
    },
  });

  return { mutate, isPending, error, reset };
};
