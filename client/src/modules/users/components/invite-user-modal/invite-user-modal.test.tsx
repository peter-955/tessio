import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishUsers from "@/lib/i18n/locales/en/users.json";
import { screen, waitFor } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiPost } from "../../test/mocks/api-client.mock";
import { setCurrentUserRole } from "../../test/mocks/current-user.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { chooseSelectOption, readSelectOption } from "../../test/utils/choose-select-option.util";
import { renderWithProviders } from "../../test/utils/render-with-providers.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import { createWorkspaceUser } from "../../test/utils/workspace-user.fixture";
import { InviteUserModal } from "./invite-user-modal";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("../../test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

const { invite } = englishUsers;

const fillForm = async (user: UserEvent, email: string, name: string): Promise<void> => {
  await user.type(screen.getByRole("textbox", { name: new RegExp(`^${invite.email}`) }), email);
  await user.type(screen.getByRole("textbox", { name: new RegExp(`^${invite.name}`) }), name);
};

const submit = async (user: UserEvent): Promise<void> => {
  await user.click(screen.getByRole("button", { name: invite.submit }));
};

describe("InviteUserModal", () => {
  beforeAll(() => {
    stubScrollIntoView();
  });

  beforeEach(() => {
    apiPost.mockReset();
    setCurrentUserRole("owner");
  });

  it("validates the email and the name before posting", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InviteUserModal isOpened onClose={vi.fn<() => void>()} />);

    await fillForm(user, "not-an-email", "   ");
    await submit(user);

    expect(await screen.findByText(englishUsers.errors.emailInvalid)).toBeInTheDocument();
    expect(screen.getByText(englishUsers.errors.nameRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
    expect(await axe(screen.getByRole("dialog"))).toHaveNoViolations();
  });

  it("rejects a name longer than 100 characters", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InviteUserModal isOpened onClose={vi.fn<() => void>()} />);

    await fillForm(user, "ivy@example.test", "a".repeat(101));
    await submit(user);

    expect(await screen.findByText(englishUsers.errors.nameRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("posts the trimmed values, shows a toast and closes", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    respondWithRoutes(apiPost, {
      "/api/users": createSuccessResult(
        createWorkspaceUser({ email: "ivy@example.test", status: "invited" }),
        201,
      ),
    });
    renderWithProviders(<InviteUserModal isOpened onClose={onClose} />);

    await fillForm(user, "  ivy@example.test ", "  Ivy Tran  ");
    await chooseSelectOption(user, invite.role, englishUsers.workspaceRoles.admin);
    await submit(user);

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/users", {
        body: { email: "ivy@example.test", name: "Ivy Tran", workspaceRole: "admin" },
      });
    });
    expect(await screen.findByText("Invite sent to ivy@example.test")).toBeInTheDocument();
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("shows EMAIL_ALREADY_USED on the email field", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    respondWithRoutes(apiPost, { "/api/users": createErrorResult(409, "EMAIL_ALREADY_USED") });
    renderWithProviders(<InviteUserModal isOpened onClose={onClose} />);

    await fillForm(user, "ada@example.test", "Ada");
    await submit(user);

    expect(await screen.findByText(englishUsers.errors.emailUsed)).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: new RegExp(`^${invite.email}`) })).toHaveAttribute(
      "aria-invalid",
      "true",
    );
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
  });

  it("shows other errors in an alert", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { "/api/users": createErrorResult(403, "PERMISSION_DENIED") });
    renderWithProviders(<InviteUserModal isOpened onClose={vi.fn<() => void>()} />);

    await fillForm(user, "ada@example.test", "Ada");
    await submit(user);

    expect(await screen.findByRole("alert")).toHaveTextContent(englishErrors.api.PERMISSION_DENIED);
  });

  it("disables the admin role for a non-owner", async () => {
    const user = userEvent.setup();
    setCurrentUserRole("admin");
    renderWithProviders(<InviteUserModal isOpened onClose={vi.fn<() => void>()} />);

    expect(screen.getByText(invite.adminOwnerOnly)).toBeInTheDocument();
    const adminOption = await readSelectOption(
      user,
      invite.role,
      englishUsers.workspaceRoles.admin,
    );
    expect(adminOption).toHaveAttribute("data-combobox-disabled", "true");
  });
});
