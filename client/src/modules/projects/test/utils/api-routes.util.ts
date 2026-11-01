import type { ApiResponseStub } from "@/components/project-context/test/utils/api-response.util";
import type { Mock } from "vitest";
import type { ApiCall } from "../mocks/api-client.mock";

type ApiRoute =
  ApiResponseStub | ((options: unknown) => ApiResponseStub | Promise<ApiResponseStub>);

export const respondWithRoutes = (
  apiCall: Mock<ApiCall>,
  routes: Readonly<Record<string, ApiRoute>>,
): void => {
  apiCall.mockImplementation((path, options) => {
    const route = routes[path];
    if (route === undefined) {
      return Promise.reject(new Error(`No mocked response for ${path}`));
    }

    return Promise.resolve(typeof route === "function" ? route(options) : route);
  });
};

export const buildNoContentResponse = (): ApiResponseStub => {
  return { response: new Response(null, { status: 204 }) };
};

export const buildValidationErrorResponse = (field: string): ApiResponseStub => {
  return {
    error: { detail: [{ loc: ["body", field], msg: "value is not valid", type: "value_error" }] },
    response: new Response(null, { status: 422 }),
  };
};

export const waitForever = (): Promise<ApiResponseStub> => {
  return new Promise(() => {
    return;
  });
};
