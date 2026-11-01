import { createApiError } from "./create-api-error.util";

interface ApiResult<Data> {
  data?: Data;
  error?: unknown;
  response: Response;
}

export const unwrapResponse = async <Data>(request: Promise<ApiResult<Data>>): Promise<Data> => {
  const result = await request;

  if (!result.response.ok) {
    throw createApiError(result.response, result.error);
  }

  return result.data as Data;
};
