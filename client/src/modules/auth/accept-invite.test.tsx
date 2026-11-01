import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { AcceptInvitePage } from "./accept-invite";
import { apiPost } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { submitNewPassword, VALID_PASSWORD } from "./test/utils/new-password-steps.util";
import { renderWithProviders } from "./test/utils/render-with-providers.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const SUBMIT_LABEL = englishAuth.acceptInvite.submit;

describe("AcceptInvitePage", () => {
  beforeEach(() => {
    apiPost.mockReset();
    setNavigation("/invite/invite-token");
  });

  it("posts the password to the invite token and routes to the setup step", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/invites/{token}": createSuccessResult({ nextStep: "two_factor_setup_required" }),
    });
    renderWithProviders(<AcceptInvitePage token="invite-token" />);

    await submitNewPassword(VALID_PASSWORD, VALID_PASSWORD, SUBMIT_LABEL);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/two-factor/setup");
    });
    expect(apiPost).toHaveBeenCalledWith("/api/auth/invites/{token}", {
      params: { path: { token: "invite-token" } },
      body: { password: VALID_PASSWORD },
    });
  });

  it("checks the length and the confirmation before posting", async () => {
    renderWithProviders(<AcceptInvitePage token="invite-token" />);

    await submitNewPassword("short", "different", SUBMIT_LABEL);

    expect(await screen.findByText(englishAuth.errors.passwordTooShort)).toBeInTheDocument();
    expect(screen.getByText(englishAuth.errors.passwordMismatch)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows a mismatch for a long password", async () => {
    renderWithProviders(<AcceptInvitePage token="invite-token" />);

    await submitNewPassword(VALID_PASSWORD, `${VALID_PASSWORD}!`, SUBMIT_LABEL);

    expect(await screen.findByText(englishAuth.errors.passwordMismatch)).toBeInTheDocument();
    expect(screen.queryByText(englishAuth.errors.passwordTooShort)).not.toBeInTheDocument();
  });

  it("shows the invalid link state", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/invites/{token}": createErrorResult(400, "INVALID_ONE_TIME_LINK"),
    });
    renderWithProviders(<AcceptInvitePage token="expired-token" />);

    await submitNewPassword(VALID_PASSWORD, VALID_PASSWORD, SUBMIT_LABEL);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishAuth.acceptInvite.invalidLink,
    );
    expect(screen.getByRole("link", { name: englishAuth.acceptInvite.goToSignIn })).toHaveAttribute(
      "href",
      "/sign-in",
    );
  });

  it("shows a breached password inline", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/invites/{token}": createErrorResult(422, "PASSWORD_BREACHED"),
    });
    renderWithProviders(<AcceptInvitePage token="invite-token" />);

    await submitNewPassword(VALID_PASSWORD, VALID_PASSWORD, SUBMIT_LABEL);

    expect(await screen.findByRole("alert")).toHaveTextContent(englishErrors.api.PASSWORD_BREACHED);
    expect(screen.getByRole("button", { name: SUBMIT_LABEL })).toBeInTheDocument();
  });

  it("has no axe violations and submits from the keyboard", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/invites/{token}": createSuccessResult({ nextStep: "two_factor_setup_required" }),
    });
    const { container } = renderWithProviders(<AcceptInvitePage token="invite-token" />);

    expect(await axe(container)).toHaveNoViolations();
    await user.type(
      screen.getByLabelText(new RegExp(`^${englishAuth.newPassword.password}`)),
      VALID_PASSWORD,
    );
    await user.type(
      screen.getByLabelText(new RegExp(`^${englishAuth.newPassword.confirm}`)),
      VALID_PASSWORD,
    );
    await tabTo(user, screen.getByRole("button", { name: SUBMIT_LABEL }));
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/two-factor/setup");
    });
  });
});
