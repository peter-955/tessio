"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { GET_PROJECT_MEMBERS_KEY } from "@/shared/hooks/queries/use-get-project-members";
import { GET_PROJECTS_KEY } from "@/shared/hooks/queries/use-get-projects";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { GET_MEMBER_CANDIDATES_KEY } from "../queries/use-get-member-candidates";

type Result = Pick<UseMutationResult<void, ApiError, string>, "mutate" | "isPending" | "reset">;

export const useDeleteProjectMember = (projectKey: string): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, reset } = useAppMutation<void, string>({
    mutationFn: async (userId) => {
      await unwrapResponse(
        apiClient.DELETE("/api/projects/{project_key}/members/{user_id}", {
          params: { path: { project_key: projectKey, user_id: userId } },
        }),
      );
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [GET_PROJECT_MEMBERS_KEY, projectKey] });
      void queryClient.invalidateQueries({ queryKey: [GET_MEMBER_CANDIDATES_KEY, projectKey] });
      void queryClient.invalidateQueries({ queryKey: [GET_PROJECT_KEY, projectKey] });
      void queryClient.invalidateQueries({ queryKey: [GET_PROJECTS_KEY] });
    },
  });

  return { mutate, isPending, reset };
};
