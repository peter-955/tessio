import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ResetPasswordPage } from "./reset-password";
import { apiPost } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createNoContentResult,
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

const SUBMIT_LABEL = englishAuth.resetPassword.submit;

describe("ResetPasswordPage", () => {
  beforeEach(() => {
    apiPost.mockReset();
    setNavigation("/reset-password/reset-token");
  });

  it("resets the password and routes to sign in with the reset notice", async () => {
    respondWithRoutes(apiPost, { "/api/auth/password/reset": createNoContentResult() });
    renderWithProviders(<ResetPasswordPage token="reset-token" />);

    await submitNewPassword(VALID_PASSWORD, VALID_PASSWORD, SUBMIT_LABEL);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/sign-in?reason=password_reset");
    });
    expect(apiPost).toHaveBeenCalledWith("/api/auth/password/reset", {
      body: { token: "reset-token", password: VALID_PASSWORD },
    });
  });

  it("shows a mismatch without posting", async () => {
    renderWithProviders(<ResetPasswordPage token="reset-token" />);

    await submitNewPassword(VALID_PASSWORD, "another long password", SUBMIT_LABEL);

    expect(await screen.findByText(englishAuth.errors.passwordMismatch)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows the invalid link state with a link to request a new one", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/password/reset": createErrorResult(400, "INVALID_ONE_TIME_LINK"),
    });
    renderWithProviders(<ResetPasswordPage token="used-token" />);

    await submitNewPassword(VALID_PASSWORD, VALID_PASSWORD, SUBMIT_LABEL);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishAuth.resetPassword.invalidLink,
    );
    expect(
      screen.getByRole("link", { name: englishAuth.resetPassword.requestNewLink }),
    ).toHaveAttribute("href", "/forgot-password");
  });

  it("shows a weak password inline", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/password/reset": createErrorResult(422, "WEAK_PASSWORD"),
    });
    renderWithProviders(<ResetPasswordPage token="reset-token" />);

    await submitNewPassword(VALID_PASSWORD, VALID_PASSWORD, SUBMIT_LABEL);

    expect(await screen.findByRole("alert")).toHaveTextContent(englishErrors.api.WEAK_PASSWORD);
  });

  it("has no axe violations and submits from the keyboard", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/password/reset": createNoContentResult(),
    });
    const { container } = renderWithProviders(<ResetPasswordPage token="reset-token" />);

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
      expect(routerReplace).toHaveBeenCalledWith("/sign-in?reason=password_reset");
    });
  });
});
