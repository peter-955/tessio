import type { ApiResult } from "@/modules/auth/test/utils/api-result.util";
import { vi } from "vitest";

export type ApiCall = (path: string, options?: unknown) => Promise<ApiResult>;

export const apiGet = vi.fn<ApiCall>();

export const apiPatch = vi.fn<ApiCall>();

export const apiClientMock = {
  apiClient: { GET: apiGet, PATCH: apiPatch },
};
