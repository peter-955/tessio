import type { ApiErrorCode } from "@/lib/api/typing/types/api-error-code.type";
import type { Mock } from "vitest";

export interface ApiResult {
  data?: unknown;
  error?: unknown;
  response: Response;
}

type ApiRoutes = Readonly<Record<string, ApiResult | (() => ApiResult)>>;

const SUCCESS_STATUS = 200;
const NO_CONTENT_STATUS = 204;

export const createSuccessResult = (data: unknown): ApiResult => {
  return { data, response: new Response(null, { status: SUCCESS_STATUS }) };
};

export const createNoContentResult = (): ApiResult => {
  return { response: new Response(null, { status: NO_CONTENT_STATUS }) };
};

export const createErrorResult = (status: number, code: ApiErrorCode): ApiResult => {
  return { error: { code, message: code }, response: new Response(null, { status }) };
};

export const respondWithRoutes = (
  apiCall: Mock<(path: string, options?: unknown) => Promise<ApiResult>>,
  routes: ApiRoutes,
): void => {
  apiCall.mockImplementation((path) => {
    const route = routes[path];
    if (route === undefined) {
      return Promise.reject(new Error(`No mocked response for ${path}`));
    }

    return Promise.resolve(typeof route === "function" ? route() : route);
  });
};
