"use client";

import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { GET_PROJECT_MEMBERS_KEY } from "@/shared/hooks/queries/use-get-project-members";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import type { ProjectMemberChange } from "../../typing/types/project-member-change.type";
import { GET_MEMBER_CANDIDATES_KEY } from "../queries/use-get-member-candidates";

type Result = Pick<
  UseMutationResult<ProjectMember, ApiError, ProjectMemberChange>,
  "mutate" | "isPending" | "reset"
>;

export const usePutProjectMember = (projectKey: string): Result => {
  const queryClient = useQueryClient();
  const { mutate, isPending, reset } = useAppMutation<ProjectMember, ProjectMemberChange>({
    mutationFn: ({ userId, role }) => {
      return unwrapResponse(
        apiClient.PUT("/api/projects/{project_key}/members/{user_id}", {
          params: { path: { project_key: projectKey, user_id: userId } },
          body: { role },
        }),
      );
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: [GET_PROJECT_MEMBERS_KEY, projectKey] }),
        queryClient.invalidateQueries({ queryKey: [GET_MEMBER_CANDIDATES_KEY, projectKey] }),
        queryClient.invalidateQueries({ queryKey: [GET_PROJECT_KEY, projectKey] }),
      ]);
    },
  });

  return { mutate, isPending, reset };
};
