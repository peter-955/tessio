import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ForgotPasswordPage } from "./forgot-password";
import { apiPost } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createNoContentResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { renderWithProviders } from "./test/utils/render-with-providers.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

describe("ForgotPasswordPage", () => {
  beforeEach(() => {
    apiPost.mockReset();
    setNavigation("/forgot-password");
  });

  it("posts the email and shows the sent state", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { "/api/auth/password/forgot": createNoContentResult() });
    renderWithProviders(<ForgotPasswordPage />);

    await user.type(
      screen.getByLabelText(new RegExp(`^${englishAuth.forgotPassword.email}`)),
      "ada@example.test",
    );
    await user.click(screen.getByRole("button", { name: englishAuth.forgotPassword.submit }));

    expect(await screen.findByRole("status")).toHaveTextContent(
      "If an account exists for ada@example.test, we sent a link. It is valid for 30 minutes.",
    );
    expect(apiPost).toHaveBeenCalledWith("/api/auth/password/forgot", {
      body: { email: "ada@example.test" },
    });
    expect(
      screen.getByRole("link", { name: englishAuth.forgotPassword.backToSignIn }),
    ).toHaveAttribute("href", "/sign-in");
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("validates the email before posting", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ForgotPasswordPage />);

    await user.type(
      screen.getByLabelText(new RegExp(`^${englishAuth.forgotPassword.email}`)),
      "not-an-email",
    );
    await user.click(screen.getByRole("button", { name: englishAuth.forgotPassword.submit }));

    expect(await screen.findByText(englishAuth.errors.emailInvalid)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows an API error inline", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/password/forgot": createErrorResult(403, "ORIGIN_NOT_ALLOWED"),
    });
    renderWithProviders(<ForgotPasswordPage />);

    await user.type(
      screen.getByLabelText(new RegExp(`^${englishAuth.forgotPassword.email}`)),
      "ada@example.test",
    );
    await user.click(screen.getByRole("button", { name: englishAuth.forgotPassword.submit }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishErrors.api.ORIGIN_NOT_ALLOWED,
    );
  });

  it("has no axe violations and submits from the keyboard", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { "/api/auth/password/forgot": createNoContentResult() });
    const { container } = renderWithProviders(<ForgotPasswordPage />);

    expect(await axe(container)).toHaveNoViolations();
    await user.type(
      screen.getByLabelText(new RegExp(`^${englishAuth.forgotPassword.email}`)),
      "ada@example.test",
    );
    await tabTo(user, screen.getByRole("button", { name: englishAuth.forgotPassword.submit }));
    await user.keyboard("{Enter}");

    expect(await screen.findByRole("status")).toBeInTheDocument();
    expect(apiPost).toHaveBeenCalledWith("/api/auth/password/forgot", {
      body: { email: "ada@example.test" },
    });
    expect(await axe(container)).toHaveNoViolations();
  });
});
