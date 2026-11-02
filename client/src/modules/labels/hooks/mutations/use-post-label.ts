"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { LabelMutationOptions } from "../../typing/types/label-mutation-options.type";
import type { CreateLabelRequest, Label } from "../../typing/types/label.type";
import { GET_LABELS_KEY } from "../queries/use-get-labels";

type Options = LabelMutationOptions<Label, CreateLabelRequest>;

export const usePostLabel = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<Label, ApiError, CreateLabelRequest> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("labels");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<Label, CreateLabelRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/labels", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors: { CONFLICT: t("errors.nameAlreadyUsed") },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_LABELS_KEY, projectKey] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
