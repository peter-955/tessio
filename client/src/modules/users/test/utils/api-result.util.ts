import type { ApiErrorCode } from "@/lib/api/typing/types/api-error-code.type";
import type { Mock } from "vitest";

export interface ApiResult {
  data?: unknown;
  error?: unknown;
  response: Response;
}

type ApiRoute = ApiResult | ((options: unknown) => ApiResult | Promise<ApiResult>);

type ApiRoutes = Readonly<Record<string, ApiRoute>>;

const SUCCESS_STATUS = 200;
const NO_CONTENT_STATUS = 204;

export const createSuccessResult = (data: unknown, status = SUCCESS_STATUS): ApiResult => {
  return { data, response: new Response(null, { status }) };
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
  apiCall.mockImplementation(async (path, options) => {
    const route = routes[path];
    if (route === undefined) {
      throw new Error(`No mocked response for ${path}`);
    }

    return typeof route === "function" ? route(options) : route;
  });
};
