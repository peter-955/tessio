import type { ApiResult } from "@/modules/labels/test/utils/api-result.util";
import { vi } from "vitest";

export type ApiCall = (path: string, options?: unknown) => Promise<ApiResult>;

export const apiGet = vi.fn<ApiCall>();

export const apiPost = vi.fn<ApiCall>();

export const apiPatch = vi.fn<ApiCall>();

export const apiDelete = vi.fn<ApiCall>();

export const apiClientMock = {
  apiClient: { GET: apiGet, POST: apiPost, PATCH: apiPatch, DELETE: apiDelete },
};
