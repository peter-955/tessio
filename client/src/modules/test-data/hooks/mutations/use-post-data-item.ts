"use client";

import { apiClient } from "@/lib/api/api-client";
import type { ApiError } from "@/lib/api/api-error";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useQueryClient, type UseMutationResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { CreateDataItemRequest, DataItem } from "../../typing/types/data-item.type";
import type { TestDataMutationOptions } from "../../typing/types/test-data-mutation-options.type";
import { GET_TEST_DATA_KEY } from "../queries/use-get-test-data";

type Options = TestDataMutationOptions<DataItem, CreateDataItemRequest>;

export const usePostDataItem = (
  projectKey: string,
  options: Options = {},
): UseMutationResult<DataItem, ApiError, CreateDataItemRequest> => {
  const queryClient = useQueryClient();
  const { t } = useTranslation("testData");
  const { onSuccess, ...mutationOptions } = options;

  return useAppMutation<DataItem, CreateDataItemRequest>({
    ...mutationOptions,
    mutationFn: (body) => {
      return unwrapResponse(
        apiClient.POST("/api/projects/{project_key}/test-data", {
          params: { path: { project_key: projectKey } },
          body,
        }),
      );
    },
    apiErrors: { TEST_DATA_KEY_ALREADY_USED: t("errors.keyAlreadyUsed") },
    onSuccess: async (data, variables, onMutateResult, context) => {
      await queryClient.invalidateQueries({ queryKey: [GET_TEST_DATA_KEY] });

      return onSuccess?.(data, variables, onMutateResult, context);
    },
  });
};
