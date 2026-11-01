import type { ApiErrorCode } from "@/lib/api/typing/types/api-error-code.type";

export const CREATE_PROJECT_FIELD_ERROR_CODES: ReadonlySet<ApiErrorCode> = new Set([
  "PROJECT_KEY_ALREADY_USED",
  "JIRA_PROJECT_ALREADY_LINKED",
]);
