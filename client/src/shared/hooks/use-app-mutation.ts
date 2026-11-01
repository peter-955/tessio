"use client";

import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import {
  useMutation,
  type UseMutationOptions,
  type UseMutationResult,
} from "@tanstack/react-query";

interface Options<Data, Variables, OnMutateResult> extends UseMutationOptions<
  Data,
  ApiError,
  Variables,
  OnMutateResult
> {
  apiErrors?: ApiErrorMessages;
  isGlobalErrorToastDisabled?: boolean;
}

export const useAppMutation = <Data, Variables = void, OnMutateResult = unknown>(
  options: Options<Data, Variables, OnMutateResult>,
): UseMutationResult<Data, ApiError, Variables, OnMutateResult> => {
  const { apiErrors, isGlobalErrorToastDisabled = false, onError, ...mutationOptions } = options;
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();

  return useMutation({
    ...mutationOptions,
    onError: (error, variables, onMutateResult, context) => {
      if (!isGlobalErrorToastDisabled) {
        showErrorToast(resolveMessage(error, apiErrors));
      }

      return onError?.(error, variables, onMutateResult, context);
    },
  });
};
