import { afterEach, describe, expect, it, vi } from "vitest";
import { createQueryClient, getOrCreateQueryClient } from "./query-client";
import { QUERY_STALE_TIME_IN_MILLISECONDS } from "./typing/constants/query-client.constant";

describe("query client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("reuses one client in the browser", () => {
    expect(getOrCreateQueryClient()).toBe(getOrCreateQueryClient());
  });

  it("creates a new client for each server render", () => {
    vi.stubGlobal("window", undefined);

    expect(getOrCreateQueryClient()).not.toBe(getOrCreateQueryClient());
  });

  it("disables retries and focus refetches", () => {
    const defaultOptions = createQueryClient().getDefaultOptions();

    expect(defaultOptions.queries?.retry).toBe(false);
    expect(defaultOptions.queries?.refetchOnWindowFocus).toBe(false);
    expect(defaultOptions.queries?.staleTime).toBe(QUERY_STALE_TIME_IN_MILLISECONDS);
    expect(defaultOptions.mutations?.retry).toBe(false);
  });
});
