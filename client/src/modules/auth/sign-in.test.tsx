import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SignInPage } from "./sign-in";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { createCurrentUser } from "./test/utils/current-user.fixture";
import { renderWithProviders } from "./test/utils/render-with-providers.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const fillAndSubmit = async (): Promise<void> => {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/^Email/), " ada@example.test ");
  await user.type(screen.getByLabelText(/^Password/), "correct horse battery");
  await user.click(screen.getByRole("button", { name: englishAuth.signIn.submit }));
};

describe("SignInPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    setNavigation("/sign-in");
    respondWithRoutes(apiGet, { "/api/auth/me": createErrorResult(401, "NOT_SIGNED_IN") });
  });

  it("renders the form without accessibility violations", async () => {
    const { container } = renderWithProviders(<SignInPage />);

    expect(screen.getByRole("heading", { name: englishAuth.signIn.title })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: englishAuth.signIn.forgotPassword })).toHaveAttribute(
      "href",
      "/forgot-password",
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("posts the trimmed email and password", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/sign-in": createSuccessResult({ nextStep: "signed_in" }),
    });
    renderWithProviders(<SignInPage />);

    await fillAndSubmit();

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/auth/sign-in", {
        body: { email: "ada@example.test", password: "correct horse battery" },
      });
    });
  });

  it.each([
    ["signed_in", "/projects/SHOP/runs?status=failed"],
    ["two_factor_required", "/two-factor?next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed"],
    [
      "two_factor_setup_required",
      "/two-factor/setup?next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed",
    ],
  ])("routes %s and keeps next", async (nextStep, expectedPath) => {
    setNavigation("/sign-in", "next=%2Fprojects%2FSHOP%2Fruns%3Fstatus%3Dfailed");
    respondWithRoutes(apiPost, { "/api/auth/sign-in": createSuccessResult({ nextStep }) });
    renderWithProviders(<SignInPage />);

    await fillAndSubmit();

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(expectedPath);
    });
  });

  it("falls back to the home page for an unsafe next", async () => {
    setNavigation("/sign-in", "next=%2F%2Fevil.com");
    respondWithRoutes(apiPost, {
      "/api/auth/sign-in": createSuccessResult({ nextStep: "signed_in" }),
    });
    renderWithProviders(<SignInPage />);

    await fillAndSubmit();

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/");
    });
  });

  it("shows invalid credentials inline", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/sign-in": createErrorResult(401, "INVALID_CREDENTIALS"),
    });
    renderWithProviders(<SignInPage />);

    await fillAndSubmit();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishErrors.api.INVALID_CREDENTIALS,
    );
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("validates the fields before posting", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SignInPage />);

    await user.click(screen.getByRole("button", { name: englishAuth.signIn.submit }));

    expect(await screen.findByText(englishAuth.errors.emailInvalid)).toBeInTheDocument();
    expect(screen.getByText(englishAuth.errors.required)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("shows the expired notice", () => {
    setNavigation("/sign-in", "reason=expired");
    renderWithProviders(<SignInPage />);

    expect(screen.getByRole("alert")).toHaveTextContent(englishAuth.signIn.expired);
  });

  it("shows the password reset notice", () => {
    setNavigation("/sign-in", "reason=password_reset");
    renderWithProviders(<SignInPage />);

    expect(screen.getByRole("status")).toHaveTextContent(englishAuth.signIn.passwordReset);
  });

  it("leaves for next when the session is already signed in", async () => {
    setNavigation("/sign-in", "next=%2Fprojects%2FSHOP%2Fruns");
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    renderWithProviders(<SignInPage />);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
    });
  });
});
