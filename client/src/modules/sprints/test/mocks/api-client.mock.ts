import { vi } from "vitest";
import type { ApiResult } from "../utils/api-result.util";

export type ApiCall = (path: string, options?: unknown) => Promise<ApiResult>;

export const apiGet = vi.fn<ApiCall>();

export const apiPost = vi.fn<ApiCall>();

export const apiPut = vi.fn<ApiCall>();

export const apiDelete = vi.fn<ApiCall>();

export const apiClientMock = {
  apiClient: { GET: apiGet, POST: apiPost, PUT: apiPut, DELETE: apiDelete },
};
