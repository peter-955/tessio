import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishNotifications from "@/lib/i18n/locales/en/notifications.json";
import {
  createErrorResult,
  createNoContentResult,
  createSuccessResult,
  type ApiResult,
} from "@/modules/auth/test/utils/api-result.util";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RouterContext } from "next/dist/shared/lib/router-context.shared-runtime";
import type { NextRouter } from "next/dist/shared/lib/router/router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GET_UNREAD_NOTIFICATION_COUNT_KEY } from "../../hooks/queries/use-get-unread-notification-count";
import { apiGet, apiPut } from "../../test/mocks/api-client.mock";
import { createNextRouter } from "../../test/utils/next-router.fixture";
import {
  createFailureNotification,
  createGapNotification,
  createNotificationPage,
  createReportNotification,
  createRunNotification,
} from "../../test/utils/notification.fixture";
import type { NotificationPage } from "../../typing/types/notification.type";
import { NotificationBell } from "./notification-bell";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListQuery {
  unreadOnly: boolean;
  cursor: string | null;
  limit: number;
}

interface ListOptions {
  params: { query: ListQuery };
}

const COUNT_PATH = "/api/notifications/unread-count";
const LIST_PATH = "/api/notifications";
const READ_PATH = "/api/notifications/{notification_id}/read";
const READ_ALL_PATH = "/api/notifications/read-all";
const BELL_LABEL = englishNotifications.bell.label;
const PANEL_TITLE = englishNotifications.panel.title;

const GAP_NOTIFICATION = createGapNotification();
const FAILURE_NOTIFICATION = createFailureNotification();
const RUN_NOTIFICATION = createRunNotification({
  isRead: true,
  readAt: "2026-11-01T10:00:00Z",
});
const ALL_NOTIFICATIONS = [GAP_NOTIFICATION, FAILURE_NOTIFICATION, RUN_NOTIFICATION];

let countResult: () => ApiResult;
let listResult: (query: ListQuery) => ApiResult;

const isListOptions = (options: unknown): options is ListOptions => {
  return typeof options === "object" && options !== null && "params" in options;
};

const respondWithCount = (count: number): void => {
  countResult = (): ApiResult => {
    return createSuccessResult({ count });
  };
};

const respondWithPages = (pagesByCursor: Readonly<Record<string, NotificationPage>>): void => {
  listResult = (query: ListQuery): ApiResult => {
    const page = pagesByCursor[query.cursor ?? "first"];
    if (page === undefined) {
      throw new Error(`No mocked page for cursor ${String(query.cursor)}`);
    }

    return createSuccessResult(page);
  };
};

const listQueries = (): ListQuery[] => {
  return apiGet.mock.calls.flatMap(([path, options]) => {
    return path === LIST_PATH && isListOptions(options) ? [options.params.query] : [];
  });
};

const countCallCount = (): number => {
  return apiGet.mock.calls.filter(([path]) => {
    return path === COUNT_PATH;
  }).length;
};

const renderBell = (): ReturnType<typeof renderWithProviders> & { router: NextRouter } => {
  const router = createNextRouter();
  const result = renderWithProviders(
    <RouterContext.Provider value={router}>
      <NotificationBell />
    </RouterContext.Provider>,
  );

  return { ...result, router };
};

const openDrawer = async (label: string): Promise<HTMLElement> => {
  const user = userEvent.setup();
  await user.click(await screen.findByRole("button", { name: label }));

  return screen.findByRole("dialog", { name: PANEL_TITLE });
};

const findList = async (dialog: HTMLElement): Promise<HTMLElement> => {
  return within(dialog).findByRole("list", { name: PANEL_TITLE });
};

describe("NotificationBell", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    respondWithCount(3);
    respondWithPages({ first: createNotificationPage(ALL_NOTIFICATIONS) });
    apiGet.mockImplementation((path, options) => {
      if (path === COUNT_PATH) {
        return Promise.resolve(countResult());
      }
      if (path === LIST_PATH && isListOptions(options)) {
        return Promise.resolve(listResult(options.params.query));
      }

      return Promise.reject(new Error(`No mocked response for ${path}`));
    });
    apiPut.mockResolvedValue(createNoContentResult());
  });

  it("shows the unread count in the label and the badge", async () => {
    renderBell();

    expect(
      await screen.findByRole("button", { name: "Notifications, 3 unread" }),
    ).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("shows no badge when nothing is unread", async () => {
    respondWithCount(0);
    renderBell();

    await waitFor(() => {
      expect(countCallCount()).toBe(1);
    });
    expect(await screen.findByRole("button", { name: BELL_LABEL })).toBeInTheDocument();
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("caps the badge at 99+", async () => {
    respondWithCount(150);
    renderBell();

    expect(
      await screen.findByRole("button", { name: "Notifications, 150 unread" }),
    ).toBeInTheDocument();
    expect(screen.getByText("99+")).toBeInTheDocument();
  });

  it("shows no badge and no toast when the count fails", async () => {
    countResult = (): ApiResult => {
      return createErrorResult(500, "INVALID_REQUEST");
    };
    renderBell();

    await waitFor(() => {
      expect(countCallCount()).toBe(1);
    });
    expect(await screen.findByRole("button", { name: BELL_LABEL })).toBeInTheDocument();
    expect(screen.queryByText(englishErrors.api.INVALID_REQUEST)).not.toBeInTheDocument();
    expect(screen.queryByText(englishErrors.unexpected)).not.toBeInTheDocument();
  });

  it("opens the drawer and lists one item of each kind with its link", async () => {
    renderBell();

    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);

    expect(listQueries()).toEqual([{ unreadOnly: false, cursor: null, limit: 20 }]);
    expect(within(list).getByText("Gap assigned to you on TES-42")).toBeInTheDocument();
    expect(within(list).getByText("Which currency applies to refunds?")).toBeInTheDocument();
    expect(within(list).getByText("Failure assigned to you on TES-43")).toBeInTheDocument();
    expect(within(list).getByText("TC-7 · Refund in euros")).toBeInTheDocument();
    expect(within(list).getByText("Run failed on TES-44")).toBeInTheDocument();
    expect(within(list).getByText("5 passed · 2 failed · 1 blocked")).toBeInTheDocument();
    expect(within(list).getAllByText("Tessio")).toHaveLength(3);
    expect(within(list).getAllByText("by Lan Nguyen")).toHaveLength(3);
    expect(list.querySelectorAll("time")).toHaveLength(3);
    expect(list.querySelector("time")).toHaveAttribute("datetime", GAP_NOTIFICATION.createdAt);
    expect(
      within(list)
        .getAllByRole("link")
        .map((link) => {
          return link.getAttribute("href");
        }),
    ).toEqual([
      "/projects/TES/stories/TES-42?tab=gaps",
      "/projects/TES/failures/1f6c8b3e-0a9d-4e4f-9b7a-8c9d0e1f2a07",
      "/projects/TES/runs/4c9f1e6b-3d2a-4b7c-8e0d-1f2a3b4c5d10",
    ]);
  });

  it("marks an unread item read when it is opened and closes the drawer", async () => {
    const user = userEvent.setup();
    const { router } = renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);

    await user.click(
      within(list).getByRole("link", { name: /^Unread: Gap assigned to you on TES-42/ }),
    );

    expect(apiPut).toHaveBeenCalledWith(READ_PATH, {
      params: { path: { notification_id: GAP_NOTIFICATION.id } },
    });
    expect(router.push).toHaveBeenCalledWith(
      "/projects/TES/stories/TES-42?tab=gaps",
      "/projects/TES/stories/TES-42?tab=gaps",
      expect.anything(),
    );
    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: PANEL_TITLE })).not.toBeInTheDocument();
    });
    await waitFor(() => {
      expect(countCallCount()).toBe(2);
    });
  });

  it("sends no read request when a read item is opened", async () => {
    const user = userEvent.setup();
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);

    await user.click(within(list).getByRole("link", { name: /^Run failed on TES-44/ }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: PANEL_TITLE })).not.toBeInTheDocument();
    });
    expect(apiPut).not.toHaveBeenCalled();
  });

  it("keeps the drawer open on a modified click but still marks the item read", async () => {
    const user = userEvent.setup();
    const { router } = renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);
    const link = within(list).getByRole("link", { name: /^Unread: Failure assigned/ });
    const preventBrowserNavigation = (event: MouseEvent): void => {
      event.preventDefault();
    };
    document.addEventListener("click", preventBrowserNavigation);

    await user.keyboard("{Control>}");
    await user.click(link);
    await user.keyboard("{/Control}");
    document.removeEventListener("click", preventBrowserNavigation);

    expect(apiPut).toHaveBeenCalledWith(READ_PATH, {
      params: { path: { notification_id: FAILURE_NOTIFICATION.id } },
    });
    expect(router.push).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog", { name: PANEL_TITLE })).toBeInTheDocument();
  });

  it("downloads a ready report from its notification and marks it read", async () => {
    const user = userEvent.setup();
    const reportNotification = createReportNotification();
    const filePath = "/api/projects/{project_key}/files/{file_id}";
    const downloadUrl = "https://files.example.test/story-TES-42.pdf";
    const openWindow = vi.spyOn(window, "open").mockReturnValue(null);
    respondWithPages({ first: createNotificationPage([reportNotification]) });
    const listAndCount = apiGet.getMockImplementation();
    apiGet.mockImplementation((path, options) => {
      if (path === filePath) {
        return Promise.resolve(
          createSuccessResult({ url: downloadUrl, expiresAt: "2026-11-01T11:00:00Z" }),
        );
      }

      return listAndCount === undefined
        ? Promise.reject(new Error(`No mocked response for ${path}`))
        : listAndCount(path, options);
    });
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);

    expect(
      within(list).getByRole("link", { name: /Report ready: TES-42 Refund a payment/ }),
    ).toHaveAttribute("href", "/projects/TES/stories/TES-42");
    await user.click(
      within(list).getByRole("button", { name: englishNotifications.item.download }),
    );

    await waitFor(() => {
      expect(openWindow).toHaveBeenCalledWith(downloadUrl, "_blank", "noopener");
    });
    expect(apiGet).toHaveBeenCalledWith(filePath, {
      params: {
        path: { project_key: "TES", file_id: "0c5f7e2b-9d8a-4b3c-8f6e-7a8b9c0d1e16" },
      },
    });
    expect(apiPut).toHaveBeenCalledWith(READ_PATH, {
      params: { path: { notification_id: reportNotification.id } },
    });
  });

  it("offers Mark as read only on unread items", async () => {
    const user = userEvent.setup();
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);
    const items = within(list).getAllByRole("listitem");

    expect(within(items[0]).getByRole("button", { name: "Mark as read" })).toBeInTheDocument();
    expect(within(items[1]).getByRole("button", { name: "Mark as read" })).toBeInTheDocument();
    expect(within(items[2]).queryByRole("button", { name: "Mark as read" })).toBeNull();

    await user.click(within(items[1]).getByRole("button", { name: "Mark as read" }));

    expect(apiPut).toHaveBeenCalledWith(READ_PATH, {
      params: { path: { notification_id: FAILURE_NOTIFICATION.id } },
    });
    expect(screen.getByRole("dialog", { name: PANEL_TITLE })).toBeInTheDocument();
    await waitFor(() => {
      expect(listQueries()).toHaveLength(2);
    });
  });

  it("marks all notifications read and refreshes the count and list", async () => {
    const user = userEvent.setup();
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    await findList(dialog);
    respondWithCount(0);

    await user.click(
      within(dialog).getByRole("button", { name: englishNotifications.panel.markAllRead }),
    );

    expect(apiPut).toHaveBeenCalledWith(READ_ALL_PATH);
    await waitFor(() => {
      expect(countCallCount()).toBe(2);
    });
    await waitFor(() => {
      expect(listQueries()).toHaveLength(2);
    });
    expect(await screen.findByRole("button", { name: BELL_LABEL })).toBeInTheDocument();
  });

  it("disables Mark all as read when nothing is unread", async () => {
    respondWithCount(0);
    renderBell();
    const dialog = await openDrawer(BELL_LABEL);
    await findList(dialog);

    expect(
      within(dialog).getByRole("button", { name: englishNotifications.panel.markAllRead }),
    ).toBeDisabled();
  });

  it("filters unread notifications and shows both empty states", async () => {
    const user = userEvent.setup();
    respondWithPages({ first: createNotificationPage([]) });
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");

    expect(
      await within(dialog).findByText(englishNotifications.empty.allTitle),
    ).toBeInTheDocument();
    expect(within(dialog).getByText(englishNotifications.empty.allDescription)).toBeInTheDocument();

    await user.click(
      within(dialog).getByRole("radio", { name: englishNotifications.panel.filterUnread }),
    );

    expect(
      await within(dialog).findByText(englishNotifications.empty.unreadTitle),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByText(englishNotifications.empty.unreadDescription),
    ).toBeInTheDocument();
    expect(listQueries()).toEqual([
      { unreadOnly: false, cursor: null, limit: 20 },
      { unreadOnly: true, cursor: null, limit: 20 },
    ]);
  });

  it("shows an error with a retry when the list fails", async () => {
    const user = userEvent.setup();
    listResult = (): ApiResult => {
      return createErrorResult(500, "INVALID_REQUEST");
    };
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");

    const alert = await within(dialog).findByRole("alert");
    expect(within(alert).getByText(englishNotifications.error.title)).toBeInTheDocument();
    expect(screen.queryByText(englishErrors.api.INVALID_REQUEST)).not.toBeInTheDocument();

    respondWithPages({ first: createNotificationPage(ALL_NOTIFICATIONS) });
    await user.click(within(alert).getByRole("button", { name: englishNotifications.error.retry }));

    expect(await findList(dialog)).toBeInTheDocument();
    expect(listQueries()).toHaveLength(2);
  });

  it("loads the next page with the cursor and hides Load more on the last page", async () => {
    const user = userEvent.setup();
    respondWithPages({
      first: createNotificationPage([GAP_NOTIFICATION], "c1"),
      c1: createNotificationPage([FAILURE_NOTIFICATION]),
    });
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    const list = await findList(dialog);
    expect(within(list).getAllByRole("listitem")).toHaveLength(1);

    await user.click(
      within(dialog).getByRole("button", { name: englishNotifications.panel.loadMore }),
    );

    await waitFor(() => {
      expect(within(list).getAllByRole("listitem")).toHaveLength(2);
    });
    expect(listQueries()).toEqual([
      { unreadOnly: false, cursor: null, limit: 20 },
      { unreadOnly: false, cursor: "c1", limit: 20 },
    ]);
    expect(within(list).getByText("Failure assigned to you on TES-43")).toBeInTheDocument();
    expect(
      within(dialog).queryByRole("button", { name: englishNotifications.panel.loadMore }),
    ).not.toBeInTheDocument();
  });

  it("updates the label when the unread count is invalidated by a live event", async () => {
    const { queryClient } = renderBell();
    expect(
      await screen.findByRole("button", { name: "Notifications, 3 unread" }),
    ).toBeInTheDocument();
    respondWithCount(4);

    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: [GET_UNREAD_NOTIFICATION_COUNT_KEY] });
    });

    expect(
      await screen.findByRole("button", { name: "Notifications, 4 unread" }),
    ).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("has no axe violations with the drawer open", async () => {
    renderBell();
    const dialog = await openDrawer("Notifications, 3 unread");
    await findList(dialog);

    expect(await axe(dialog)).toHaveNoViolations();
  });
});
