import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishStories from "@/lib/i18n/locales/en/stories.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { act, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GET_STORIES_KEY } from "../../hooks/queries/use-get-stories";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "../../test/utils/api-result.util";
import { interpolate } from "../../test/utils/interpolate.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
  VIEWER_CAPABILITIES,
} from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { buildSyncState } from "../../test/utils/story-fixture.util";
import { SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS } from "../../typing/constants/sync.constant";
import type { ProjectSyncState } from "../../typing/types/story.type";
import { SyncControl } from "./sync-control";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

const SYNC_PATH = "/api/projects/{project_key}/sync";
const { sync } = englishStories;

const minutesAgo = (minutes: number): string => {
  return new Date(Date.now() - minutes * 60000).toISOString();
};

const respondWithSyncState = (state: ProjectSyncState | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [SYNC_PATH]: typeof state === "function" ? state : createSuccessResult(state),
  });
};

const countSyncRequests = (): number => {
  return apiGet.mock.calls.filter(([path]) => {
    return path === SYNC_PATH;
  }).length;
};

const renderControl = (capabilities = ADMIN_CAPABILITIES): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<SyncControl />, buildProject({ capabilities }));
};

describe("SyncControl", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows never synced with the sync button", async () => {
    respondWithSyncState(buildSyncState());
    renderControl();

    expect(await screen.findByText(sync.never)).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent(sync.never);
    expect(screen.getByRole("button", { name: sync.action })).toBeEnabled();
  });

  it("hides the button without the jira.sync capability", async () => {
    respondWithSyncState(buildSyncState());
    renderControl(VIEWER_CAPABILITIES);

    expect(await screen.findByText(sync.never)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: sync.action })).toBeNull();
  });

  it("shows queued and running as in progress", async () => {
    respondWithSyncState(buildSyncState({ status: "queued", queuedAt: minutesAgo(1) }));
    const { unmount } = renderControl();

    expect(await screen.findByText(sync.queued)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: sync.action })).toBeDisabled();
    unmount();

    respondWithSyncState(
      buildSyncState({ status: "running", queuedAt: minutesAgo(2), startedAt: minutesAgo(1) }),
    );
    renderControl();

    expect(await screen.findByText(sync.running)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: sync.action })).toBeDisabled();
  });

  it("shows the last sync time", async () => {
    respondWithSyncState(
      buildSyncState({
        status: "succeeded",
        finishedAt: "2026-10-20T09:30:00Z",
        lastSucceededAt: "2026-10-20T09:30:00Z",
      }),
    );
    renderControl();

    expect(
      await screen.findByText(interpolate(sync.succeeded, { date: "Oct 20, 09:30 AM UTC" })),
    ).toBeInTheDocument();
  });

  it("shows the failure reason and the last success", async () => {
    respondWithSyncState(
      buildSyncState({
        status: "failed",
        finishedAt: "2026-10-20T09:30:00Z",
        lastSucceededAt: "2026-10-19T08:00:00Z",
        errorCode: "JIRA_NOT_CONFIGURED",
      }),
    );
    renderControl();

    expect(
      await screen.findByText(
        interpolate(sync.failed, { reason: englishErrors.api.JIRA_NOT_CONFIGURED }),
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByText(interpolate(sync.lastSucceeded, { date: "Oct 19, 08:00 AM UTC" })),
    ).toBeInTheDocument();
  });

  it("falls back to the unexpected reason without an error code", async () => {
    respondWithSyncState(buildSyncState({ status: "failed" }));
    renderControl();

    expect(
      await screen.findByText(interpolate(sync.failed, { reason: englishErrors.unexpected })),
    ).toBeInTheDocument();
  });

  it("shows a stale sync and lets it be requested again", async () => {
    respondWithSyncState(
      buildSyncState({ status: "running", queuedAt: minutesAgo(30), startedAt: minutesAgo(20) }),
    );
    renderControl();

    expect(await screen.findByText(sync.stale)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: sync.action })).toBeEnabled();
  });

  it("shows when the status cannot be loaded", async () => {
    respondWithSyncState(() => {
      return createErrorResult(500, "CONFLICT");
    });
    renderControl();

    expect(await screen.findByText(sync.unavailable)).toBeInTheDocument();
  });

  it("requests a sync and shows it as queued", async () => {
    const user = userEvent.setup();
    respondWithSyncState(buildSyncState());
    let resolvePost: (result: ApiResult) => void = () => {
      return;
    };
    apiPost.mockImplementation(() => {
      return new Promise((resolve) => {
        resolvePost = resolve;
      });
    });
    renderControl();

    await user.click(await screen.findByRole("button", { name: sync.action }));

    expect(apiPost).toHaveBeenCalledWith(SYNC_PATH, {
      params: { path: { project_key: "SHOP" } },
    });
    await waitFor(() => {
      expect(screen.getByRole("button", { name: sync.action })).toBeDisabled();
    });
    await act(async () => {
      resolvePost(
        createSuccessResult(buildSyncState({ status: "queued", queuedAt: minutesAgo(0) })),
      );
      await Promise.resolve();
    });
    expect(await screen.findByText(sync.queued)).toBeInTheDocument();
  });

  it("shows the Jira not configured message", async () => {
    const user = userEvent.setup();
    respondWithSyncState(buildSyncState());
    respondWithRoutes(apiPost, { [SYNC_PATH]: createErrorResult(409, "JIRA_NOT_CONFIGURED") });
    renderControl();

    await user.click(await screen.findByRole("button", { name: sync.action }));

    expect(await screen.findByText(englishStories.errors.jiraNotConfigured)).toBeInTheDocument();
  });

  it("polls only while a sync is in progress and refreshes data when it succeeds", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    let state = buildSyncState({ status: "running", queuedAt: minutesAgo(1) });
    respondWithSyncState(() => {
      return createSuccessResult(state);
    });
    const { queryClient } = renderControl();
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");

    expect(await screen.findByText(sync.running)).toBeInTheDocument();
    expect(countSyncRequests()).toBe(1);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS);
    });
    expect(countSyncRequests()).toBe(2);

    state = buildSyncState({
      status: "succeeded",
      finishedAt: "2026-10-20T09:30:00Z",
      lastSucceededAt: "2026-10-20T09:30:00Z",
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS);
    });
    expect(
      await screen.findByText(interpolate(sync.succeeded, { date: "Oct 20, 09:30 AM UTC" })),
    ).toBeInTheDocument();
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: [GET_STORIES_KEY] });
    const requestsAfterSuccess = countSyncRequests();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS * 3);
    });
    expect(countSyncRequests()).toBe(requestsAfterSuccess);
  });

  it("has no axe violations and requests a sync from the keyboard", async () => {
    const user = userEvent.setup();
    respondWithSyncState(buildSyncState());
    apiPost.mockResolvedValue(createSuccessResult(buildSyncState({ status: "queued" })));
    const { container } = renderControl();

    const button = await screen.findByRole("button", { name: sync.action });
    expect(await axe(container)).toHaveNoViolations();
    await tabTo(user, button);
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(SYNC_PATH, expect.anything());
    });
    expect(await axe(container)).toHaveNoViolations();
  });
});
