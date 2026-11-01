import type { ApiError } from "@/lib/api/api-error";
import type { UseMutationOptions } from "@tanstack/react-query";

export type TestCaseMutationOptions<Data, Variables> = Omit<
  UseMutationOptions<Data, ApiError, Variables>,
  "mutationFn"
> & {
  isGlobalErrorToastDisabled?: boolean;
};
