import { ApiError } from "@/lib/api/api-error";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { renderHookWithProviders } from "@/test/utils/render-hook-with-providers.util";
import { act, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useAppMutation } from "./use-app-mutation";

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

const keyAlreadyUsedError = new ApiError({
  status: 409,
  code: "PROJECT_KEY_ALREADY_USED",
  message: "Project key already used.",
});

const rejectWithKeyAlreadyUsed = (): Promise<string> => {
  return Promise.reject(keyAlreadyUsedError);
};

describe("useAppMutation", () => {
  it("returns the data without a toast", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppMutation<string, string>({
        mutationFn: (name) => {
          return Promise.resolve(name.toUpperCase());
        },
      });
    });

    act(() => {
      result.current.mutate("tes");
    });

    await waitFor(() => {
      expect(result.current.data).toBe("TES");
    });
    expect(showErrorToast).not.toHaveBeenCalled();
  });

  it("shows the translated message and still calls the caller's onError", async () => {
    const onError = vi.fn();
    const { result } = renderHookWithProviders(() => {
      return useAppMutation<string, string>({
        mutationFn: rejectWithKeyAlreadyUsed,
        onError,
      });
    });

    act(() => {
      result.current.mutate("TES");
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
    expect(showErrorToast).toHaveBeenCalledTimes(1);
    expect(showErrorToast).toHaveBeenCalledWith(englishErrors.api.PROJECT_KEY_ALREADY_USED);
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError.mock.calls[0]?.[0]).toBe(keyAlreadyUsedError);
    expect(onError.mock.calls[0]?.[1]).toBe("TES");
    expect(onError.mock.calls[0]).toHaveLength(4);
  });

  it("prefers the caller's message for the error code", async () => {
    const { result } = renderHookWithProviders(() => {
      return useAppMutation<string, string>({
        mutationFn: rejectWithKeyAlreadyUsed,
        apiErrors: { PROJECT_KEY_ALREADY_USED: "Pick another project key." },
      });
    });

    act(() => {
      result.current.mutate("TES");
    });

    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith("Pick another project key.");
    });
  });

  it("shows no toast when the global toast is disabled", async () => {
    const onError = vi.fn();
    const { result } = renderHookWithProviders(() => {
      return useAppMutation<string, string>({
        mutationFn: rejectWithKeyAlreadyUsed,
        onError,
        isGlobalErrorToastDisabled: true,
      });
    });

    act(() => {
      result.current.mutate("TES");
    });

    await waitFor(() => {
      expect(onError).toHaveBeenCalledTimes(1);
    });
    expect(showErrorToast).not.toHaveBeenCalled();
  });
});
