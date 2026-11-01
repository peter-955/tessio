import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { createCurrentUser } from "./test/utils/current-user.fixture";
import { renderWithProviders } from "./test/utils/render-with-providers.util";
import { TwoFactorPage } from "./two-factor";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const findFirstDigitInput = async (): Promise<HTMLElement> => {
  const label = `${englishAuth.twoFactor.codeLabel}, digit 1 of 6`;

  return screen.findByLabelText(label);
};

describe("TwoFactorPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    setNavigation("/two-factor", "next=%2Fprojects%2FSHOP%2Fruns");
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("two_factor_required")),
    });
  });

  it("submits automatically after 6 digits and goes to next", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor": createSuccessResult({ nextStep: "signed_in" }),
    });
    renderWithProviders(<TwoFactorPage />);

    await user.click(await findFirstDigitInput());
    await user.keyboard("123456");

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/auth/two-factor", { body: { code: "123456" } });
    });
    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
    });
  });

  it("verifies a recovery code", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor": createSuccessResult({ nextStep: "signed_in" }),
    });
    renderWithProviders(<TwoFactorPage />);

    await user.click(
      await screen.findByRole("button", { name: englishAuth.twoFactor.useRecoveryCode }),
    );
    const input = screen.getByLabelText(new RegExp(`^${englishAuth.twoFactor.recoveryCodeLabel}`));
    expect(input).toHaveAttribute("autocomplete", "one-time-code");
    expect(input).toHaveAttribute("placeholder", "xxxxx-xxxxx");
    await user.type(input, "abcde-12345");
    await user.click(screen.getByRole("button", { name: englishAuth.twoFactor.submit }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/auth/two-factor", {
        body: { code: "abcde-12345" },
      });
    });
    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
    });
  });

  it("shows an invalid code inline and clears the input", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor": createErrorResult(401, "INVALID_TWO_FACTOR_CODE"),
    });
    renderWithProviders(<TwoFactorPage />);

    const firstDigitInput = await findFirstDigitInput();
    await user.click(firstDigitInput);
    await user.keyboard("654321");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishErrors.api.INVALID_TWO_FACTOR_CODE,
    );
    expect(firstDigitInput).toHaveValue("");
    expect(routerReplace).not.toHaveBeenCalled();
  });

  it("shows a locked sign-in as an alert", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor": createErrorResult(429, "SIGN_IN_LOCKED"),
    });
    renderWithProviders(<TwoFactorPage />);

    await user.click(await findFirstDigitInput());
    await user.keyboard("111111");

    expect(await screen.findByRole("alert")).toHaveTextContent(englishErrors.api.SIGN_IN_LOCKED);
  });

  it("asks for all 6 digits before posting", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TwoFactorPage />);

    await user.click(await findFirstDigitInput());
    await user.keyboard("12");
    await user.click(screen.getByRole("button", { name: englishAuth.twoFactor.submit }));

    expect(await screen.findByRole("alert")).toHaveTextContent(englishAuth.errors.codeIncomplete);
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("sends an expired half session back to sign in", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor": createErrorResult(401, "NOT_SIGNED_IN"),
    });
    renderWithProviders(<TwoFactorPage />);

    await user.click(await findFirstDigitInput());
    await user.keyboard("123456");

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(
        "/sign-in?next=%2Fprojects%2FSHOP%2Fruns&reason=expired",
      );
    });
  });

  it("redirects a session that still needs setup", async () => {
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("two_factor_setup_required")),
    });
    renderWithProviders(<TwoFactorPage />);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(
        "/two-factor/setup?next=%2Fprojects%2FSHOP%2Fruns",
      );
    });
  });

  it("redirects a missing session to sign in as expired", async () => {
    respondWithRoutes(apiGet, { "/api/auth/me": createErrorResult(401, "NOT_SIGNED_IN") });
    renderWithProviders(<TwoFactorPage />);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith(
        "/sign-in?next=%2Fprojects%2FSHOP%2Fruns&reason=expired",
      );
    });
  });

  it("has no axe violations and submits the code from the keyboard", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor": createSuccessResult({ nextStep: "signed_in" }),
    });
    const { container } = renderWithProviders(<TwoFactorPage />);

    const firstDigit = await findFirstDigitInput();
    expect(await axe(container)).toHaveNoViolations();
    await tabTo(user, firstDigit);
    await user.keyboard("123456");

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
    });
  });
});
