import { describe, expect, it } from "vitest";
import { buildSyncState } from "../test/utils/story-fixture.util";
import { checkIsSyncInProgress, checkIsSyncStale } from "./sync-status.util";

const NOW = new Date("2026-10-20T10:00:00Z");

describe("checkIsSyncInProgress", () => {
  it("is false without a state or for finished states", () => {
    expect(checkIsSyncInProgress(undefined, NOW)).toBe(false);
    expect(checkIsSyncInProgress(buildSyncState(), NOW)).toBe(false);
    expect(
      checkIsSyncInProgress(
        buildSyncState({ status: "succeeded", queuedAt: "2026-10-20T09:59:00Z" }),
        NOW,
      ),
    ).toBe(false);
    expect(checkIsSyncInProgress(buildSyncState({ status: "failed" }), NOW)).toBe(false);
  });

  it("is true for a recent queued or running sync", () => {
    expect(
      checkIsSyncInProgress(
        buildSyncState({ status: "queued", queuedAt: "2026-10-20T09:50:00Z" }),
        NOW,
      ),
    ).toBe(true);
    expect(
      checkIsSyncInProgress(
        buildSyncState({
          status: "running",
          queuedAt: "2026-10-20T09:00:00Z",
          startedAt: "2026-10-20T09:58:00Z",
        }),
        NOW,
      ),
    ).toBe(true);
  });

  it("treats a sync older than 15 minutes as stale", () => {
    const staleState = buildSyncState({
      status: "running",
      queuedAt: "2026-10-20T09:40:00Z",
      startedAt: "2026-10-20T09:45:00Z",
    });

    expect(checkIsSyncInProgress(staleState, NOW)).toBe(false);
    expect(checkIsSyncStale(staleState, NOW)).toBe(true);
    expect(checkIsSyncStale(buildSyncState({ status: "queued" }), NOW)).toBe(true);
    expect(checkIsSyncStale(buildSyncState({ status: "succeeded" }), NOW)).toBe(false);
  });
});
