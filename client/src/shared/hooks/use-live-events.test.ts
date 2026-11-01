import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { QueryClientProvider, type QueryClient } from "@tanstack/react-query";
import { act, renderHook } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useLiveEvents } from "./use-live-events";

vi.mock("@/shared/typing/constants/live-event-query-keys.constant", () => {
  return { LIVE_EVENT_QUERY_KEYS: { "run.finished": ["GET_RUNS_KEY", "GET_RUN_KEY"] } };
});

class FakeEventSource {
  static instances: FakeEventSource[] = [];

  readonly url: string;
  isClosed = false;
  private readonly listeners = new Map<string, Set<() => void>>();

  constructor(url: string) {
    this.url = url;
    FakeEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: () => void): void {
    const listeners = this.listeners.get(type) ?? new Set<() => void>();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }

  removeEventListener(type: string, listener: () => void): void {
    this.listeners.get(type)?.delete(listener);
  }

  close(): void {
    this.isClosed = true;
  }

  emit(type: string): void {
    this.listeners.get(type)?.forEach((listener) => {
      listener();
    });
  }

  countListeners(): number {
    return [...this.listeners.values()].reduce((count, listeners) => {
      return count + listeners.size;
    }, 0);
  }
}

interface HookProps {
  isEnabled: boolean;
  onStreamClosed: () => void;
}

interface RenderedLiveEvents {
  queryClient: QueryClient;
  rerender: (props: HookProps) => void;
  unmount: () => void;
}

const renderLiveEvents = (initialProps: HookProps): RenderedLiveEvents => {
  const queryClient = createTestQueryClient();
  const { rerender, unmount } = renderHook(
    (props: HookProps) => {
      useLiveEvents(props);
    },
    {
      initialProps,
      wrapper: ({ children }: { children: ReactNode }) => {
        return createElement(QueryClientProvider, { client: queryClient }, children);
      },
    },
  );

  return { queryClient, rerender, unmount };
};

const getLatestSource = (): FakeEventSource => {
  const source = FakeEventSource.instances.at(-1);
  if (source === undefined) {
    throw new Error("No event source was opened.");
  }

  return source;
};

const failAndWait = (delayInMilliseconds: number): void => {
  const openedCount = FakeEventSource.instances.length;
  act(() => {
    getLatestSource().emit("error");
  });
  act(() => {
    vi.advanceTimersByTime(delayInMilliseconds - 1);
  });
  expect(FakeEventSource.instances).toHaveLength(openedCount);
  act(() => {
    vi.advanceTimersByTime(1);
  });
  expect(FakeEventSource.instances).toHaveLength(openedCount + 1);
};

describe("useLiveEvents", () => {
  beforeEach(() => {
    FakeEventSource.instances = [];
    vi.useFakeTimers();
    vi.stubGlobal("EventSource", FakeEventSource);
    vi.spyOn(Math, "random").mockReturnValue(0);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("opens the stream and invalidates the mapped keys for an event", () => {
    const onStreamClosed = vi.fn();
    const { queryClient } = renderLiveEvents({ isEnabled: true, onStreamClosed });
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");

    expect(FakeEventSource.instances).toHaveLength(1);
    expect(getLatestSource().url).toBe("/api/events");

    act(() => {
      getLatestSource().emit("ready");
      getLatestSource().emit("run.finished");
    });

    expect(invalidateQueries).toHaveBeenCalledTimes(2);
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["GET_RUNS_KEY"] });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["GET_RUN_KEY"] });
    expect(onStreamClosed).not.toHaveBeenCalled();
  });

  it("closes on error and reconnects with a capped exponential backoff", () => {
    const onStreamClosed = vi.fn();
    renderLiveEvents({ isEnabled: true, onStreamClosed });

    const firstSource = getLatestSource();
    failAndWait(1000);
    expect(firstSource.isClosed).toBe(true);
    expect(firstSource.countListeners()).toBe(0);
    expect(onStreamClosed).toHaveBeenCalledTimes(1);

    [2000, 4000, 8000, 16000, 30000, 30000].forEach((delayInMilliseconds) => {
      failAndWait(delayInMilliseconds);
    });
    expect(onStreamClosed).toHaveBeenCalledTimes(7);
  });

  it("adds up to 20 percent jitter to the delay", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.5);
    renderLiveEvents({ isEnabled: true, onStreamClosed: vi.fn() });

    failAndWait(1100);
  });

  it("invalidates every query after a reconnect and resets the delay", () => {
    const { queryClient } = renderLiveEvents({ isEnabled: true, onStreamClosed: vi.fn() });
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");

    act(() => {
      getLatestSource().emit("ready");
    });
    expect(invalidateQueries).not.toHaveBeenCalled();

    failAndWait(1000);
    failAndWait(2000);
    act(() => {
      getLatestSource().emit("ready");
    });
    expect(invalidateQueries).toHaveBeenCalledTimes(1);
    expect(invalidateQueries).toHaveBeenCalledWith();

    failAndWait(1000);
  });

  it("reconnects at once when the browser comes back online", () => {
    renderLiveEvents({ isEnabled: true, onStreamClosed: vi.fn() });

    act(() => {
      getLatestSource().emit("error");
    });
    act(() => {
      window.dispatchEvent(new Event("online"));
    });
    expect(FakeEventSource.instances).toHaveLength(2);

    act(() => {
      vi.advanceTimersByTime(60000);
    });
    expect(FakeEventSource.instances).toHaveLength(2);
  });

  it("opens nothing when it is disabled", () => {
    renderLiveEvents({ isEnabled: false, onStreamClosed: vi.fn() });

    expect(FakeEventSource.instances).toHaveLength(0);
  });

  it("closes the stream on unmount", () => {
    const { unmount } = renderLiveEvents({ isEnabled: true, onStreamClosed: vi.fn() });
    const source = getLatestSource();

    unmount();

    expect(source.isClosed).toBe(true);
    expect(source.countListeners()).toBe(0);
  });

  it("clears a pending reconnect on unmount", () => {
    const { unmount } = renderLiveEvents({ isEnabled: true, onStreamClosed: vi.fn() });
    act(() => {
      getLatestSource().emit("error");
    });

    unmount();
    act(() => {
      vi.advanceTimersByTime(60000);
      window.dispatchEvent(new Event("online"));
    });

    expect(FakeEventSource.instances).toHaveLength(1);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("closes the stream when it becomes disabled", () => {
    const { rerender } = renderLiveEvents({ isEnabled: true, onStreamClosed: vi.fn() });
    const source = getLatestSource();

    rerender({ isEnabled: false, onStreamClosed: vi.fn() });

    expect(source.isClosed).toBe(true);
  });

  it("calls the latest onStreamClosed without reopening the stream", () => {
    const firstOnStreamClosed = vi.fn();
    const latestOnStreamClosed = vi.fn();
    const { rerender } = renderLiveEvents({ isEnabled: true, onStreamClosed: firstOnStreamClosed });

    rerender({ isEnabled: true, onStreamClosed: latestOnStreamClosed });
    act(() => {
      getLatestSource().emit("error");
    });

    expect(FakeEventSource.instances).toHaveLength(1);
    expect(firstOnStreamClosed).not.toHaveBeenCalled();
    expect(latestOnStreamClosed).toHaveBeenCalledTimes(1);
  });
});
