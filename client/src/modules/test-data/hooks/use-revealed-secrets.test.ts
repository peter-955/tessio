import { act, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiPost } from "../test/mocks/api-client.mock";
import { createSuccessResult } from "../test/utils/api-result.util";
import { renderHookWithClient } from "../test/utils/render-hook-with-client.util";
import { SECRET_REVEAL_DURATION_IN_MILLISECONDS } from "../typing/constants/test-data.constant";
import { useRevealedSecrets } from "./use-revealed-secrets";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../test/mocks/api-client.mock")).apiClientMock;
});

const ITEM_ID = "a1000000-0000-4000-8000-000000000009";

describe("useRevealedSecrets", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    apiPost.mockReset();
    apiPost.mockResolvedValue(createSuccessResult({ value: "s3cret" }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows the value after reveal and hides it after 30 seconds", async () => {
    const { result, queryClient } = renderHookWithClient(() => {
      return useRevealedSecrets("SHOP");
    });

    await act(async () => {
      await result.current.reveal(ITEM_ID);
    });

    expect(apiPost).toHaveBeenCalledWith("/api/projects/{project_key}/test-data/{item_id}/reveal", {
      params: { path: { project_key: "SHOP", item_id: ITEM_ID } },
    });
    expect(result.current.revealedValueById).toEqual({ [ITEM_ID]: "s3cret" });
    expect(result.current.isRevealing(ITEM_ID)).toBe(false);
    expect(JSON.stringify(queryClient.getQueryCache().getAll())).not.toContain("s3cret");

    act(() => {
      vi.advanceTimersByTime(SECRET_REVEAL_DURATION_IN_MILLISECONDS - 1);
    });
    expect(result.current.revealedValueById[ITEM_ID]).toBe("s3cret");

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current.revealedValueById).toEqual({});
  });

  it("restarts the timer on a second reveal", async () => {
    const { result } = renderHookWithClient(() => {
      return useRevealedSecrets("SHOP");
    });

    await act(async () => {
      await result.current.reveal(ITEM_ID);
    });
    act(() => {
      vi.advanceTimersByTime(20000);
    });
    await act(async () => {
      await result.current.reveal(ITEM_ID);
    });
    act(() => {
      vi.advanceTimersByTime(20000);
    });

    expect(result.current.revealedValueById[ITEM_ID]).toBe("s3cret");

    act(() => {
      vi.advanceTimersByTime(10000);
    });
    expect(result.current.revealedValueById).toEqual({});
  });

  it("hides a value on request", async () => {
    const { result } = renderHookWithClient(() => {
      return useRevealedSecrets("SHOP");
    });

    await act(async () => {
      await result.current.reveal(ITEM_ID);
    });
    act(() => {
      result.current.hide(ITEM_ID);
    });

    expect(result.current.revealedValueById).toEqual({});
  });

  it("clears the hide timer on unmount", async () => {
    const setTimeoutSpy = vi.spyOn(globalThis, "setTimeout");
    const clearTimeoutSpy = vi.spyOn(globalThis, "clearTimeout");
    const { result, unmount } = renderHookWithClient(() => {
      return useRevealedSecrets("SHOP");
    });

    await act(async () => {
      await result.current.reveal(ITEM_ID);
    });
    const hideTimerIndex = setTimeoutSpy.mock.calls.findIndex(
      ([, delay]) => delay === SECRET_REVEAL_DURATION_IN_MILLISECONDS,
    );
    const hideTimer = setTimeoutSpy.mock.results[hideTimerIndex]?.value as unknown;
    unmount();

    expect(hideTimerIndex).toBeGreaterThanOrEqual(0);
    expect(clearTimeoutSpy).toHaveBeenCalledWith(hideTimer);
  });

  it("reports the pending reveal", async () => {
    let resolveReveal: (value: ReturnType<typeof createSuccessResult>) => void = () => {
      return;
    };
    apiPost.mockReturnValue(
      new Promise((resolve) => {
        resolveReveal = resolve;
      }),
    );
    const { result } = renderHookWithClient(() => {
      return useRevealedSecrets("SHOP");
    });

    act(() => {
      void result.current.reveal(ITEM_ID);
    });
    await waitFor(() => {
      expect(result.current.isRevealing(ITEM_ID)).toBe(true);
    });

    await act(async () => {
      resolveReveal(createSuccessResult({ value: "s3cret" }));
      await Promise.resolve();
    });
    await waitFor(() => {
      expect(result.current.isRevealing(ITEM_ID)).toBe(false);
    });
  });
});
