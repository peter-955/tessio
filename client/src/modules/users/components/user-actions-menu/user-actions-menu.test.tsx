import englishUsers from "@/lib/i18n/locales/en/users.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import { setCurrentUserRole } from "../../test/mocks/current-user.mock";
import {
  createErrorResult,
  createNoContentResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { openActionsMenu, readMenuItemNames } from "../../test/utils/open-actions-menu.util";
import { renderWithProviders } from "../../test/utils/render-with-providers.util";
import { ADMIN_ID, createWorkspaceUser, OWNER_ID } from "../../test/utils/workspace-user.fixture";
import type { UserConfirmAction } from "../../typing/types/user-action.type";
import type { WorkspaceUser } from "../../typing/types/workspace-user.type";
import { UserActionsMenu } from "./user-actions-menu";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("../../test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

const { actions } = englishUsers;

const OTHER_ADMIN_ID = "9b8e5cda-8db0-4f4c-9b9a-4eaf6fc08c09";

const renderMenu = (
  target: WorkspaceUser,
  isOnAccessPage = false,
): { onConfirm: ReturnType<typeof vi.fn<(action: UserConfirmAction) => void>> } => {
  const onConfirm = vi.fn<(action: UserConfirmAction) => void>();
  renderWithProviders(
    <UserActionsMenu
      user={target}
      onConfirm={onConfirm}
      onChangeRole={vi.fn<() => void>()}
      isOnAccessPage={isOnAccessPage}
    />,
  );

  return { onConfirm };
};

const readItems = async (target: WorkspaceUser, isOnAccessPage = false): Promise<string[]> => {
  renderMenu(target, isOnAccessPage);
  const menu = await openActionsMenu(userEvent.setup(), target.name);

  return readMenuItemNames(menu);
};

describe("UserActionsMenu", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    setCurrentUserRole("owner");
  });

  it("offers resend and deactivate for an invited user", async () => {
    const items = await readItems(
      createWorkspaceUser({ status: "invited", isTwoFactorSetUp: false }),
    );

    expect(items).toEqual([actions.viewAccess, actions.resendInvite, actions.deactivate]);
  });

  it("offers reset two-factor for an active user only when it is set up", async () => {
    const items = await readItems(createWorkspaceUser({ isTwoFactorSetUp: true }));

    expect(items).toEqual([
      actions.viewAccess,
      actions.changeRole,
      actions.resetTwoFactor,
      actions.deactivate,
    ]);
  });

  it("hides reset two-factor for an active user without it", async () => {
    const items = await readItems(createWorkspaceUser({ isTwoFactorSetUp: false }));

    expect(items).toEqual([actions.viewAccess, actions.changeRole, actions.deactivate]);
  });

  it("offers reactivate for a deactivated user", async () => {
    const items = await readItems(createWorkspaceUser({ status: "deactivated" }));

    expect(items).toEqual([actions.viewAccess, actions.reactivate]);
  });

  it("shows only view access to an admin acting on another admin", async () => {
    setCurrentUserRole("admin");
    const items = await readItems(
      createWorkspaceUser({ id: OTHER_ADMIN_ID, name: "Other Admin", workspaceRole: "admin" }),
    );

    expect(items).toEqual([actions.viewAccess]);
  });

  it("offers change role only to the owner", async () => {
    setCurrentUserRole("admin");
    const items = await readItems(createWorkspaceUser());

    expect(items).toEqual([actions.viewAccess, actions.resetTwoFactor, actions.deactivate]);
  });

  it("has no manage items on the self row", async () => {
    setCurrentUserRole("admin");
    const items = await readItems(
      createWorkspaceUser({ id: ADMIN_ID, name: "Me Admin", workspaceRole: "admin" }),
    );

    expect(items).toEqual([actions.viewAccess]);
  });

  it("has no manage items on the owner row", async () => {
    setCurrentUserRole("admin");
    const items = await readItems(
      createWorkspaceUser({ id: OWNER_ID, name: "The Owner", workspaceRole: "owner" }),
    );

    expect(items).toEqual([actions.viewAccess]);
  });

  it("links view access to the access page", async () => {
    const target = createWorkspaceUser();
    renderMenu(target);
    const menu = await openActionsMenu(userEvent.setup(), target.name);

    expect(
      within(menu).getByRole("menuitem", { name: actions.viewAccess, hidden: true }),
    ).toHaveAttribute("href", `/users/${target.id}`);
  });

  it("omits view access on the access page", async () => {
    const items = await readItems(createWorkspaceUser({ isTwoFactorSetUp: false }), true);

    expect(items).toEqual([actions.changeRole, actions.deactivate]);
  });

  it("asks for confirmation before deactivating", async () => {
    const user = userEvent.setup();
    const target = createWorkspaceUser();
    const { onConfirm } = renderMenu(target);
    const menu = await openActionsMenu(user, target.name);

    await user.click(
      within(menu).getByRole("menuitem", { name: actions.deactivate, hidden: true }),
    );

    expect(onConfirm).toHaveBeenCalledWith("deactivate");
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("resends an invite at once and shows a toast", async () => {
    const user = userEvent.setup();
    const target = createWorkspaceUser({ status: "invited", email: "ivy@example.test" });
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/resend-invite": createNoContentResult(),
    });
    renderMenu(target);
    const menu = await openActionsMenu(user, target.name);

    await user.click(
      within(menu).getByRole("menuitem", { name: actions.resendInvite, hidden: true }),
    );

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/users/{user_id}/resend-invite", {
        params: { path: { user_id: target.id } },
      });
    });
    expect(await screen.findByText("Invite sent again to ivy@example.test")).toBeInTheDocument();
  });

  it("shows the translated error when the user already accepted", async () => {
    const user = userEvent.setup();
    const target = createWorkspaceUser({ status: "invited" });
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/resend-invite": createErrorResult(409, "USER_NOT_INVITED"),
    });
    renderMenu(target);
    const menu = await openActionsMenu(user, target.name);

    await user.click(
      within(menu).getByRole("menuitem", { name: actions.resendInvite, hidden: true }),
    );

    expect(await screen.findByText(englishUsers.errors.notInvited)).toBeInTheDocument();
  });

  it("opens from the keyboard and has no axe violations", async () => {
    const user = userEvent.setup();
    const target = createWorkspaceUser();
    const { container } = renderWithProviders(
      <UserActionsMenu
        user={target}
        onConfirm={vi.fn<(action: UserConfirmAction) => void>()}
        onChangeRole={vi.fn<() => void>()}
        isOnAccessPage={false}
      />,
    );

    const trigger = screen.getByRole("button", { name: `Actions for ${target.name}` });
    expect(await axe(container)).toHaveNoViolations();
    await tabTo(user, trigger);
    await user.keyboard("{Enter}");

    const menu = await screen.findByRole("menu", { hidden: true });
    expect(trigger).toHaveAttribute("aria-expanded", "true");
    expect(await axe(menu)).toHaveNoViolations();
    expect(readMenuItemNames(menu)).toContain(actions.deactivate);
  });
});
