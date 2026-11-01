import { renderHookWithProviders } from "@/test/utils/render-hook-with-providers.util";
import { act, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiPost } from "../../test/mocks/api-client.mock";
import { routerReplace } from "../../test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createNoContentResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { usePostSignOut } from "./use-post-sign-out";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

describe("usePostSignOut", () => {
  beforeEach(() => {
    apiPost.mockReset();
  });

  it("clears every cached query and goes to sign in", async () => {
    respondWithRoutes(apiPost, { "/api/auth/sign-out": createNoContentResult() });
    const { result, queryClient } = renderHookWithProviders(() => {
      return usePostSignOut();
    });
    queryClient.setQueryData(["GET_PROJECTS_KEY"], ["TES"]);

    act(() => {
      result.current.mutate();
    });

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/sign-in");
    });
    expect(apiPost).toHaveBeenCalledWith("/api/auth/sign-out");
    expect(queryClient.getQueryData(["GET_PROJECTS_KEY"])).toBeUndefined();
  });

  it("also leaves when the session had already ended", async () => {
    respondWithRoutes(apiPost, { "/api/auth/sign-out": createErrorResult(401, "NOT_SIGNED_IN") });
    const { result } = renderHookWithProviders(() => {
      return usePostSignOut();
    });

    act(() => {
      result.current.mutate();
    });

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/sign-in");
    });
  });
});
