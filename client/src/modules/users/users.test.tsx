import englishUsers from "@/lib/i18n/locales/en/users.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { setCurrentUserRole } from "./test/mocks/current-user.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { chooseSelectOption } from "./test/utils/choose-select-option.util";
import { openActionsMenu } from "./test/utils/open-actions-menu.util";
import { renderWithProviders } from "./test/utils/render-with-providers.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { ADMIN_ID, createWorkspaceUser } from "./test/utils/workspace-user.fixture";
import { UsersPage } from "./users";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("./test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface UserListRequest {
  params: { query: Record<string, string> };
}

const USERS = [
  createWorkspaceUser({
    id: ADMIN_ID,
    name: "Ada Admin",
    email: "ada@example.test",
    workspaceRole: "admin",
  }),
  createWorkspaceUser({
    id: "7f6c3ab8-6b9e-4d2a-9f7e-2c8b4dae6a07",
    name: "Ivy Invited",
    email: "ivy@example.test",
    status: "invited",
    isTwoFactorSetUp: false,
  }),
  createWorkspaceUser({
    id: "8a7d4bc9-7caf-4e3b-8a8f-3d9c5ebf7b08",
    name: "Dan Deactivated",
    email: "dan@example.test",
    status: "deactivated",
    isTwoFactorSetUp: false,
  }),
];

const readListQueries = (): Record<string, string>[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === "/api/users";
    })
    .map(([, options]) => {
      return (options as UserListRequest).params.query;
    });
};

describe("UsersPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    setCurrentUserRole("admin");
    respondWithRoutes(apiGet, { "/api/users": createSuccessResult(USERS) });
  });

  it("shows the no-access state to a member and never requests users", async () => {
    setCurrentUserRole("member");
    const { container } = renderWithProviders(<UsersPage />);

    expect(screen.getByText(englishUsers.noAccess.title)).toBeInTheDocument();
    expect(screen.getByText(englishUsers.noAccess.description)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("lists users with their role, status and two-factor labels", async () => {
    const { container } = renderWithProviders(<UsersPage />);

    expect(screen.getByRole("heading", { name: englishUsers.title })).toBeInTheDocument();
    const adminRow = (await screen.findByRole("link", { name: "Ada Admin" })).closest("tr");
    expect(adminRow).not.toBeNull();
    const adminCells = within(adminRow as HTMLElement);
    expect(adminCells.getByText(englishUsers.you)).toBeInTheDocument();
    expect(adminCells.getByText("ada@example.test")).toBeInTheDocument();
    expect(adminCells.getByText(englishUsers.workspaceRoles.admin)).toBeInTheDocument();
    expect(adminCells.getByText(englishUsers.statuses.active)).toBeInTheDocument();
    expect(adminCells.getByText(englishUsers.twoFactor.setUp)).toBeInTheDocument();

    const invitedRow = screen.getByRole("link", { name: "Ivy Invited" }).closest("tr");
    const invitedCells = within(invitedRow as HTMLElement);
    expect(invitedCells.getByText(englishUsers.statuses.invited)).toBeInTheDocument();
    expect(invitedCells.getByText("—")).toBeInTheDocument();

    const deactivatedRow = screen.getByRole("link", { name: "Dan Deactivated" }).closest("tr");
    const deactivatedCells = within(deactivatedRow as HTMLElement);
    expect(deactivatedCells.getByText(englishUsers.statuses.deactivated)).toBeInTheDocument();
    expect(deactivatedCells.getByText(englishUsers.twoFactor.notSetUp)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dan Deactivated" })).toHaveAttribute(
      "href",
      "/users/8a7d4bc9-7caf-4e3b-8a8f-3d9c5ebf7b08",
    );

    expect(await axe(container)).toHaveNoViolations();
  });

  it("sends the chosen status filter", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UsersPage />);
    await screen.findByRole("link", { name: "Ada Admin" });

    await chooseSelectOption(user, englishUsers.filters.status, englishUsers.statuses.deactivated);

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ status: "deactivated" });
    });
    expect(readListQueries()[0]).toEqual({});
  });

  it("sends the chosen role filter and maps all back to no filter", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UsersPage />);
    await screen.findByRole("link", { name: "Ada Admin" });

    await chooseSelectOption(user, englishUsers.filters.role, englishUsers.workspaceRoles.member);

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ workspaceRole: "member" });
    });

    await chooseSelectOption(user, englishUsers.filters.role, englishUsers.filters.all);

    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: englishUsers.filters.role })).toHaveValue(
        englishUsers.filters.all,
      );
    });
    expect(readListQueries()).not.toContainEqual({ workspaceRole: "all" });
  });

  it("debounces the search before querying", async () => {
    const user = userEvent.setup();
    renderWithProviders(<UsersPage />);
    await screen.findByRole("link", { name: "Ada Admin" });

    await user.type(screen.getByRole("textbox", { name: englishUsers.filters.search }), " ada");

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ query: "ada" });
    });
    const searchedQueries = readListQueries().filter((query) => {
      return query.query !== undefined;
    });
    expect(searchedQueries).toEqual([{ query: "ada" }]);
  });

  it("deactivates a user after confirmation and refreshes the list", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/deactivate": createSuccessResult({
        ...USERS[1],
        status: "deactivated",
      }),
    });
    renderWithProviders(<UsersPage />);
    await screen.findByRole("link", { name: "Ivy Invited" });
    const listRequestCount = readListQueries().length;

    const menu = await openActionsMenu(user, "Ivy Invited");
    await user.click(
      within(menu).getByRole("menuitem", { name: englishUsers.actions.deactivate, hidden: true }),
    );
    expect(apiPost).not.toHaveBeenCalled();
    await user.click(
      await screen.findByRole("button", { name: englishUsers.confirm.deactivate.action }),
    );

    expect(await screen.findByText("Ivy Invited is deactivated")).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith("/api/users/{user_id}/deactivate", {
      params: { path: { user_id: USERS[1]?.id } },
    });
    await waitFor(() => {
      expect(readListQueries().length).toBeGreaterThan(listRequestCount);
    });
  });

  it("shows the empty state when nothing matches", async () => {
    respondWithRoutes(apiGet, { "/api/users": createSuccessResult([]) });
    renderWithProviders(<UsersPage />);

    expect(await screen.findByText(englishUsers.empty.title)).toBeInTheDocument();
    expect(screen.getByText(englishUsers.empty.description)).toBeInTheDocument();
  });

  it("shows the error state and retries", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/users": createErrorResult(500, "CONFLICT") });
    renderWithProviders(<UsersPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent(englishUsers.loadError);

    respondWithRoutes(apiGet, { "/api/users": createSuccessResult(USERS) });
    await user.click(screen.getByRole("button", { name: englishUsers.retry }));

    expect(await screen.findByRole("link", { name: "Ada Admin" })).toBeInTheDocument();
  });
});
