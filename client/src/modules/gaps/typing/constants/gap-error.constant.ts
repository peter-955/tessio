import type { ApiErrorCode } from "@/lib/api/typing/types/api-error-code.type";

export const INLINE_RAISE_ERROR_CODES: ReadonlySet<ApiErrorCode> = new Set([
  "UNKNOWN_REFERENCE",
  "ASSIGNEE_NOT_ACTIVE_MEMBER",
]);

export const INLINE_REASSIGN_ERROR_CODES: ReadonlySet<ApiErrorCode> = new Set([
  "ASSIGNEE_NOT_ACTIVE_MEMBER",
]);
