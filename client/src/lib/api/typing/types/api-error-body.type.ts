import type { components } from "../../openapi.type";

export type ApiErrorBody = components["schemas"]["ErrorResponse"];

export type ValidationErrorBody = components["schemas"]["HTTPValidationError"];
