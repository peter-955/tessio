"use client";

import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import {
  useQuery,
  type QueryKey,
  type UseQueryOptions,
  type UseQueryResult,
} from "@tanstack/react-query";
import { useEffect, useRef } from "react";

interface Options<Data, Key extends QueryKey> extends UseQueryOptions<Data, ApiError, Data, Key> {
  queryKey: Key;
  apiErrors?: ApiErrorMessages;
  isGlobalErrorToastDisabled?: boolean;
}

export const useAppQuery = <Data, Key extends QueryKey>(
  options: Options<Data, Key>,
): UseQueryResult<Data, ApiError> => {
  const { apiErrors, isGlobalErrorToastDisabled = false, ...queryOptions } = options;
  const result = useQuery(queryOptions);
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();
  const toastedErrorUpdatedAt = useRef(0);
  const { error, errorUpdatedAt, isError } = result;

  useEffect(() => {
    if (
      !isError ||
      isGlobalErrorToastDisabled ||
      error.code === "NOT_SIGNED_IN" ||
      toastedErrorUpdatedAt.current === errorUpdatedAt
    ) {
      return;
    }

    toastedErrorUpdatedAt.current = errorUpdatedAt;
    showErrorToast(resolveMessage(error, apiErrors));
  }, [
    apiErrors,
    error,
    errorUpdatedAt,
    isError,
    isGlobalErrorToastDisabled,
    resolveMessage,
    showErrorToast,
  ]);

  return result;
};
