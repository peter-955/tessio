import type { ApiErrorCode } from "./typing/types/api-error-code.type";

interface Options {
  status: number;
  code: ApiErrorCode | null;
  message: string;
  fieldErrors?: Readonly<Record<string, string>>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: ApiErrorCode | null;
  readonly fieldErrors: Readonly<Record<string, string>>;

  constructor({ status, code, message, fieldErrors = {} }: Options) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
  }
}
