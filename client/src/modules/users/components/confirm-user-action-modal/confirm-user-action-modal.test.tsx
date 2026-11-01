import englishUsers from "@/lib/i18n/locales/en/users.json";
import { GET_PROJECT_MEMBERS_KEY } from "@/shared/hooks/queries/use-get-project-members";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GET_WORKSPACE_USER_KEY } from "../../hooks/queries/use-get-workspace-user";
import { GET_WORKSPACE_USERS_KEY } from "../../hooks/queries/use-get-workspace-users";
import { apiPost } from "../../test/mocks/api-client.mock";
import { setCurrentUserRole } from "../../test/mocks/current-user.mock";
import { createSuccessResult, respondWithRoutes } from "../../test/utils/api-result.util";
import { renderWithProviders } from "../../test/utils/render-with-providers.util";
import { createWorkspaceUser } from "../../test/utils/workspace-user.fixture";
import { ConfirmUserActionModal } from "./confirm-user-action-modal";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("../../test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

const TARGET = createWorkspaceUser({ name: "Lan Nguyen" });

describe("ConfirmUserActionModal", () => {
  beforeEach(() => {
    apiPost.mockReset();
    setCurrentUserRole("owner");
  });

  it("renders nothing without a target", () => {
    renderWithProviders(
      <ConfirmUserActionModal user={null} action={null} onClose={vi.fn<() => void>()} />,
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("deactivates after confirmation and refreshes the lists", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    const queryClient = createTestQueryClient();
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/deactivate": createSuccessResult({
        ...TARGET,
        status: "deactivated",
      }),
    });
    renderWithProviders(
      <ConfirmUserActionModal user={TARGET} action="deactivate" onClose={onClose} />,
      queryClient,
    );

    expect(screen.getByText("Deactivate Lan Nguyen?")).toBeInTheDocument();
    expect(screen.getByText(englishUsers.confirm.deactivate.message)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: englishUsers.confirm.deactivate.action }));

    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });
    expect(apiPost).toHaveBeenCalledWith("/api/users/{user_id}/deactivate", {
      params: { path: { user_id: TARGET.id } },
    });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: [GET_WORKSPACE_USERS_KEY] });
    expect(invalidateQueries).toHaveBeenCalledWith({
      queryKey: [GET_WORKSPACE_USER_KEY, TARGET.id],
    });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: [GET_PROJECT_MEMBERS_KEY] });
    expect(await screen.findByText("Lan Nguyen is deactivated")).toBeInTheDocument();
  });

  it("shows the invited toast when reactivate sends a new invite", async () => {
    const user = userEvent.setup();
    const deactivatedUser = { ...TARGET, status: "deactivated" as const };
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/reactivate": createSuccessResult({ ...TARGET, status: "invited" }),
    });
    renderWithProviders(
      <ConfirmUserActionModal
        user={deactivatedUser}
        action="reactivate"
        onClose={vi.fn<() => void>()}
      />,
    );

    await user.click(screen.getByRole("button", { name: englishUsers.confirm.reactivate.action }));

    expect(
      await screen.findByText("Lan Nguyen is reactivated and a new invite was sent"),
    ).toBeInTheDocument();
  });

  it("shows the active toast when reactivate restores access", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/reactivate": createSuccessResult(TARGET),
    });
    renderWithProviders(
      <ConfirmUserActionModal
        user={{ ...TARGET, status: "deactivated" }}
        action="reactivate"
        onClose={vi.fn<() => void>()}
      />,
    );

    await user.click(screen.getByRole("button", { name: englishUsers.confirm.reactivate.action }));

    expect(await screen.findByText("Lan Nguyen is active again")).toBeInTheDocument();
  });

  it("resets two-factor after confirmation", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/reset-two-factor": createSuccessResult({
        ...TARGET,
        isTwoFactorSetUp: false,
      }),
    });
    renderWithProviders(
      <ConfirmUserActionModal
        user={TARGET}
        action="resetTwoFactor"
        onClose={vi.fn<() => void>()}
      />,
    );

    await user.click(
      screen.getByRole("button", { name: englishUsers.confirm.resetTwoFactor.action }),
    );

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/users/{user_id}/reset-two-factor", {
        params: { path: { user_id: TARGET.id } },
      });
    });
    expect(await screen.findByText("Two-factor reset for Lan Nguyen")).toBeInTheDocument();
  });

  it("has no axe violations and confirms from the keyboard", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    respondWithRoutes(apiPost, {
      "/api/users/{user_id}/deactivate": createSuccessResult({
        ...TARGET,
        status: "deactivated",
      }),
    });
    renderWithProviders(
      <ConfirmUserActionModal user={TARGET} action="deactivate" onClose={onClose} />,
    );

    const dialog = screen.getByRole("dialog", { name: "Deactivate Lan Nguyen?" });
    expect(await axe(dialog)).toHaveNoViolations();
    await tabTo(
      user,
      within(dialog).getByRole("button", { name: englishUsers.confirm.deactivate.action }),
    );
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });
  });

  it("closes on Escape without posting", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn<() => void>();
    renderWithProviders(
      <ConfirmUserActionModal user={TARGET} action="deactivate" onClose={onClose} />,
    );

    await screen.findByRole("dialog");
    await user.keyboard("{Escape}");

    expect(onClose).toHaveBeenCalledTimes(1);
    expect(apiPost).not.toHaveBeenCalled();
  });
});
