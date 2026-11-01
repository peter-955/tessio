import englishUsers from "@/lib/i18n/locales/en/users.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiPut } from "../../test/mocks/api-client.mock";
import { setCurrentUserRole } from "../../test/mocks/current-user.mock";
import { createSuccessResult, respondWithRoutes } from "../../test/utils/api-result.util";
import { chooseSelectOption } from "../../test/utils/choose-select-option.util";
import { renderWithProviders } from "../../test/utils/render-with-providers.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { createWorkspaceUser } from "../../test/utils/workspace-user.fixture";
import { ChangeRoleModal } from "./change-role-modal";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("../../test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

const TARGET = createWorkspaceUser({ name: "Lan Nguyen", workspaceRole: "member" });

describe("ChangeRoleModal", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiPut.mockReset();
    setCurrentUserRole("owner");
  });

  it("keeps save disabled while the role is unchanged", () => {
    renderWithProviders(<ChangeRoleModal user={TARGET} onClose={vi.fn<() => void>()} />);

    expect(screen.getByText("Change the role of Lan Nguyen")).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: englishUsers.invite.role })).toHaveValue(
      englishUsers.workspaceRoles.member,
    );
    expect(screen.getByRole("button", { name: englishUsers.changeRole.submit })).toBeDisabled();
  });

  it("puts the new role, shows a toast and closes", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    respondWithRoutes(apiPut, {
      "/api/users/{user_id}/workspace-role": createSuccessResult({
        ...TARGET,
        workspaceRole: "admin",
      }),
    });
    renderWithProviders(<ChangeRoleModal user={TARGET} onClose={onClose} />);

    await chooseSelectOption(user, englishUsers.invite.role, englishUsers.workspaceRoles.admin);
    const saveButton = screen.getByRole("button", { name: englishUsers.changeRole.submit });
    expect(saveButton).toBeEnabled();
    await user.click(saveButton);

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/users/{user_id}/workspace-role", {
        params: { path: { user_id: TARGET.id } },
        body: { workspaceRole: "admin" },
      });
    });
    expect(await screen.findByText("Lan Nguyen is now Workspace admin")).toBeInTheDocument();
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("has no axe violations, changes the role from the keyboard and closes on Escape", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    respondWithRoutes(apiPut, {
      "/api/users/{user_id}/workspace-role": createSuccessResult({
        ...TARGET,
        workspaceRole: "admin",
      }),
    });
    renderWithProviders(<ChangeRoleModal user={TARGET} onClose={onClose} />);

    const dialog = screen.getByRole("dialog");
    expect(await axe(dialog)).toHaveNoViolations();
    const combobox = screen.getByRole("combobox", { name: englishUsers.invite.role });
    await tabTo(user, combobox);
    await user.keyboard("{ArrowDown}");
    const adminOption = await screen.findByRole("option", {
      name: englishUsers.workspaceRoles.admin,
      hidden: true,
    });
    for (let step = 0; step < 4 && !adminOption.hasAttribute("data-combobox-selected"); step += 1) {
      await user.keyboard("{ArrowDown}");
    }
    await user.keyboard("{Enter}");
    expect(combobox).toHaveValue(englishUsers.workspaceRoles.admin);
    await tabTo(user, screen.getByRole("button", { name: englishUsers.changeRole.submit }));
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/users/{user_id}/workspace-role", {
        params: { path: { user_id: TARGET.id } },
        body: { workspaceRole: "admin" },
      });
    });
  });

  it("closes on Escape", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    renderWithProviders(<ChangeRoleModal user={TARGET} onClose={onClose} />);

    await screen.findByRole("dialog");
    await user.keyboard("{Escape}");

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
