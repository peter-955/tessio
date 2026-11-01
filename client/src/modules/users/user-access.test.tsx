import englishUsers from "@/lib/i18n/locales/en/users.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet } from "./test/mocks/api-client.mock";
import { setCurrentUserRole } from "./test/mocks/current-user.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { openActionsMenu, readMenuItemNames } from "./test/utils/open-actions-menu.util";
import { renderWithProviders } from "./test/utils/render-with-providers.util";
import {
  ADMIN_ID,
  OWNER_ID,
  createUserProjectAccess,
  createWorkspaceUser,
} from "./test/utils/workspace-user.fixture";
import type { WorkspaceRole } from "./typing/types/workspace-user.type";
import { UserAccessPage } from "./user-access";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("./test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const TARGET = createWorkspaceUser({ name: "Lan Nguyen", email: "lan@example.test" });

const ACCESSES = [
  createUserProjectAccess(),
  createUserProjectAccess({
    projectId: "0d9e6fdb-9e01-4a5d-8cab-5fb07ad19d10",
    projectKey: "OLD",
    projectName: "Old portal",
    role: "viewer",
    isArchived: true,
  }),
];

const { access } = englishUsers;

describe("UserAccessPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    setCurrentUserRole("owner");
    respondWithRoutes(apiGet, {
      "/api/users/{user_id}": createSuccessResult(TARGET),
      "/api/users/{user_id}/access": createSuccessResult(ACCESSES),
    });
  });

  it("lists the projects with links, role labels and the archived badge", async () => {
    const { container } = renderWithProviders(<UserAccessPage userId={TARGET.id} />);

    expect(await screen.findByRole("heading", { name: "Lan Nguyen" })).toBeInTheDocument();
    expect(screen.getByText("lan@example.test")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: access.back })).toHaveAttribute("href", "/users");
    expect(screen.getByRole("heading", { name: access.title })).toBeInTheDocument();

    const shopLink = await screen.findByRole("link", { name: "Shop checkout" });
    expect(shopLink).toHaveAttribute("href", "/projects/SHOP");
    const shopRow = within(shopLink.closest("tr") as HTMLElement);
    expect(shopRow.getByText("SHOP")).toBeInTheDocument();
    expect(shopRow.getByText(englishUsers.projectRoles.qc)).toBeInTheDocument();
    expect(shopRow.queryByText(access.archived)).not.toBeInTheDocument();

    const oldLink = screen.getByRole("link", { name: "Old portal" });
    expect(oldLink).toHaveAttribute("href", "/projects/OLD");
    const oldRow = within(oldLink.closest("tr") as HTMLElement);
    expect(oldRow.getByText(englishUsers.projectRoles.viewer)).toBeInTheDocument();
    expect(oldRow.getByText(access.archived)).toBeInTheDocument();

    expect(screen.queryByText(access.workspaceAdminNote)).not.toBeInTheDocument();
    expect(apiGet).toHaveBeenCalledWith(
      "/api/users/{user_id}/access",
      expect.objectContaining({ params: { path: { user_id: TARGET.id } } }),
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the action menu without the view access item", async () => {
    renderWithProviders(<UserAccessPage userId={TARGET.id} />);
    await screen.findByRole("heading", { name: "Lan Nguyen" });

    const menu = await openActionsMenu(userEvent.setup(), "Lan Nguyen");

    expect(readMenuItemNames(menu)).toEqual([
      englishUsers.actions.changeRole,
      englishUsers.actions.resetTwoFactor,
      englishUsers.actions.deactivate,
    ]);
  });

  it.each<{ case: string; actorRole: WorkspaceRole; targetId: string; targetRole: WorkspaceRole }>([
    { case: "their own page", actorRole: "owner", targetId: OWNER_ID, targetRole: "owner" },
    { case: "the owner", actorRole: "admin", targetId: OWNER_ID, targetRole: "owner" },
    {
      case: "another admin",
      actorRole: "admin",
      targetId: "5d4a1e96-4f7c-4b0e-9d5c-0a6f2b8c4e05",
      targetRole: "admin",
    },
    {
      case: "an admin who is themselves",
      actorRole: "admin",
      targetId: ADMIN_ID,
      targetRole: "admin",
    },
  ])(
    "hides the action menu when the actor cannot manage $case",
    async ({ actorRole, targetId, targetRole }) => {
      setCurrentUserRole(actorRole);
      respondWithRoutes(apiGet, {
        "/api/users/{user_id}": createSuccessResult({
          ...TARGET,
          id: targetId,
          workspaceRole: targetRole,
        }),
        "/api/users/{user_id}/access": createSuccessResult(ACCESSES),
      });
      renderWithProviders(<UserAccessPage userId={targetId} />);
      await screen.findByRole("heading", { name: "Lan Nguyen" });

      expect(
        screen.queryByRole("button", { name: "Actions for Lan Nguyen" }),
      ).not.toBeInTheDocument();
    },
  );

  it("adds the workspace admin note for an admin", async () => {
    respondWithRoutes(apiGet, {
      "/api/users/{user_id}": createSuccessResult({ ...TARGET, workspaceRole: "admin" }),
      "/api/users/{user_id}/access": createSuccessResult(ACCESSES),
    });
    renderWithProviders(<UserAccessPage userId={TARGET.id} />);

    expect(await screen.findByText(access.workspaceAdminNote)).toBeInTheDocument();
    expect(screen.getByText(englishUsers.workspaceRoles.admin)).toBeInTheDocument();
  });

  it("shows the not-found view on a 404", async () => {
    respondWithRoutes(apiGet, {
      "/api/users/{user_id}": createErrorResult(404, "NOT_FOUND"),
      "/api/users/{user_id}/access": createErrorResult(404, "NOT_FOUND"),
    });
    const { container } = renderWithProviders(<UserAccessPage userId="unknown" />);

    expect(await screen.findByText(access.notFound.title)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: access.back })).toHaveAttribute("href", "/users");
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the empty view when the user is in no project", async () => {
    respondWithRoutes(apiGet, {
      "/api/users/{user_id}": createSuccessResult(TARGET),
      "/api/users/{user_id}/access": createSuccessResult([]),
    });
    renderWithProviders(<UserAccessPage userId={TARGET.id} />);

    expect(await screen.findByText(access.empty.title)).toBeInTheDocument();
    expect(screen.getByText(access.empty.description)).toBeInTheDocument();
  });

  it("shows the error view with retry when the access list fails", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      "/api/users/{user_id}": createSuccessResult(TARGET),
      "/api/users/{user_id}/access": createErrorResult(500, "CONFLICT"),
    });
    renderWithProviders(<UserAccessPage userId={TARGET.id} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(access.loadError);

    respondWithRoutes(apiGet, {
      "/api/users/{user_id}": createSuccessResult(TARGET),
      "/api/users/{user_id}/access": createSuccessResult(ACCESSES),
    });
    await user.click(screen.getByRole("button", { name: englishUsers.retry }));

    expect(await screen.findByRole("link", { name: "Shop checkout" })).toBeInTheDocument();
  });

  it("shows the loading state while the queries are pending", () => {
    apiGet.mockImplementation(() => {
      return new Promise(() => {
        return;
      });
    });
    const { container } = renderWithProviders(<UserAccessPage userId={TARGET.id} />);

    expect(container.querySelectorAll('[aria-busy="true"]')).toHaveLength(2);
  });

  it("shows the no-access state to a member without requests", async () => {
    setCurrentUserRole("member");
    renderWithProviders(<UserAccessPage userId={TARGET.id} />);

    expect(screen.getByText(englishUsers.noAccess.title)).toBeInTheDocument();
    await waitFor(() => {
      expect(apiGet).not.toHaveBeenCalled();
    });
  });
});
