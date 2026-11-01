import { ApiError } from "@/lib/api/api-error";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { renderHookWithProviders } from "@/test/utils/render-hook-with-providers.util";
import { waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useAppQuery } from "./use-app-query";

const { showErrorToast } = vi.hoisted(() => {
  return { showErrorToast: vi.fn<(title: string, description?: string) => void>() };
});

vi.mock("@/shared/hooks/use-show-toast", () => {
  const toasts = {
    showErrorToast,
    showSuccessToast: vi.fn(),
    showInfoToast: vi.fn(),
    showWarningToast: vi.fn(),
  };

  return {
    useShowToast: () => {
      return toasts;
    },
  };
});

const permissionDeniedError = new ApiError({
  status: 403,
  code: "PERMISSION_DENIED",
  message: "Permission denied.",
});

const notSignedInError = new ApiError({
  status: 401,
  code: "NOT_SIGNED_IN",
  message: "Sign in to continue.",
});

describe("useAppQuery", () => {
  it("returns the data without a toast", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.resolve(["TES"]);
        },
      });
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(result.current.data).toEqual(["TES"]);
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("shows the translated message of the error code once", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.reject(permissionDeniedError);
        },
      });
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    expect(result.current.error).toBe(permissionDeniedError);
    expect(showErrorToast).toHaveBeenCalledTimes(1);
    expect(showErrorToast).toHaveBeenCalledWith(englishErrors.api.PERMISSION_DENIED);
  });

  it("prefers the caller's message for the error code", async () => {
    renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.reject(permissionDeniedError);
        },
        apiErrors: { PERMISSION_DENIED: "Only project admins can see this." },
      });
    });

    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith("Only project admins can see this.");
    });
    expect(showErrorToast).toHaveBeenCalledTimes(1);
  });

  it("shows no toast when the global toast is disabled", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.reject(permissionDeniedError);
        },
        isGlobalErrorToastDisabled: true,
      });
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("leaves an expired session to the session guard without a toast", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.reject(notSignedInError);
        },
      });
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("shows the unexpected message for an error without a code", async () => {
    renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.reject(new Error("Network down"));
        },
      });
    });

    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith(englishErrors.unexpected);
    });
  });

  it("toasts again when a refetch fails again", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppQuery({
        queryKey: ["projects"],
        queryFn: () => {
          return Promise.reject(permissionDeniedError);
        },
      });
    });

    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledTimes(1);
    });
    await result.current.refetch();
    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledTimes(2);
    });
  });
});
