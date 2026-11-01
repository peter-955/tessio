import { ApiError } from "../api-error";
import type { ApiErrorBody, ValidationErrorBody } from "../typing/types/api-error-body.type";

type ValidationErrorItem = NonNullable<ValidationErrorBody["detail"]>[number];

const isRecord = (value: unknown): value is Record<string, unknown> => {
  return typeof value === "object" && value !== null && !Array.isArray(value);
};

const isApiErrorBody = (body: unknown): body is ApiErrorBody => {
  return isRecord(body) && typeof body.code === "string" && typeof body.message === "string";
};

const isValidationErrorBody = (body: unknown): body is ValidationErrorBody => {
  return isRecord(body) && Array.isArray(body.detail);
};

const isValidationErrorItem = (item: unknown): item is ValidationErrorItem => {
  return isRecord(item) && Array.isArray(item.loc) && typeof item.msg === "string";
};

const describeStatus = (response: Response): string => {
  return response.statusText || String(response.status);
};

const createValidationApiError = (response: Response, body: ValidationErrorBody): ApiError => {
  const items = (body.detail ?? []).filter(isValidationErrorItem);
  const fieldErrors: Record<string, string> = {};

  items.forEach((item) => {
    const field = item.loc.at(-1);
    if (field !== undefined && fieldErrors[String(field)] === undefined) {
      fieldErrors[String(field)] = item.msg;
    }
  });

  return new ApiError({
    status: response.status,
    code: "INVALID_REQUEST",
    message: items[0]?.msg ?? describeStatus(response),
    fieldErrors,
  });
};

export const createApiError = (response: Response, body: unknown): ApiError => {
  if (isApiErrorBody(body)) {
    return new ApiError({ status: response.status, code: body.code, message: body.message });
  }

  if (isValidationErrorBody(body)) {
    return createValidationApiError(response, body);
  }

  return new ApiError({ status: response.status, code: null, message: describeStatus(response) });
};
