import type { ApiErrorCode } from "./api-error-code.type";

export type ApiErrorMessages = Partial<Record<ApiErrorCode, string>>;
