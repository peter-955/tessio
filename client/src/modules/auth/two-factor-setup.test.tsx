import englishAuth from "@/lib/i18n/locales/en/auth.json";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
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
import { OBJECT_URL, stubObjectUrl } from "./test/utils/stub-object-url.util";
import { TwoFactorSetupPage } from "./two-factor-setup";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const SETUP_KEY = "JBSWY3DPEHPK3PXP";
const RECOVERY_CODES = Array.from({ length: 10 }, (_value, index) => {
  return `code${index}-abcde`;
});

const countSetupCalls = (): number => {
  return apiPost.mock.calls.filter(([path]) => {
    return path === "/api/auth/two-factor/setup";
  }).length;
};

const enterConfirmCode = async (code: string): Promise<void> => {
  const user = userEvent.setup();
  await user.click(
    await screen.findByLabelText(`${englishAuth.twoFactorSetup.codeLabel}, digit 1 of 6`),
  );
  await user.keyboard(code);
};

describe("TwoFactorSetupPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    setNavigation("/two-factor/setup", "next=%2Fprojects%2FSHOP%2Fruns");
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("two_factor_setup_required")),
    });
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor/setup": createSuccessResult({
        key: SETUP_KEY,
        setupUri: `otpauth://totp/Tessio:ada?secret=${SETUP_KEY}&issuer=Tessio`,
      }),
      "/api/auth/two-factor/confirm": createSuccessResult({
        nextStep: "signed_in",
        recoveryCodes: RECOVERY_CODES,
      }),
    });
  });

  it("starts setup once under StrictMode and shows the QR code and key", async () => {
    const queryClient = createTestQueryClient();
    queryClient.setQueryData(
      ["GET_CURRENT_USER_KEY"],
      createCurrentUser("two_factor_setup_required"),
    );
    renderWithProviders(<TwoFactorSetupPage />, { queryClient, isStrictMode: true });

    expect(
      await screen.findByRole("img", { name: englishAuth.twoFactorSetup.qrCodeLabel }),
    ).toBeInTheDocument();
    expect(screen.getByText(SETUP_KEY)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy" })).toBeInTheDocument();
    expect(countSetupCalls()).toBe(1);
  });

  it("confirms the code, shows 10 codes and gates Continue on the checkbox", async () => {
    const user = userEvent.setup();
    const { createObjectURL, revokeObjectURL } = stubObjectUrl();
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {
      return;
    });
    const { queryClient } = renderWithProviders(<TwoFactorSetupPage />, { isStrictMode: true });

    await enterConfirmCode("123456");

    expect(apiPost).toHaveBeenCalledWith("/api/auth/two-factor/confirm", {
      body: { code: "123456" },
    });
    const list = await screen.findByRole("list", { name: englishAuth.recoveryCodes.listLabel });
    expect(list.querySelectorAll("li")).toHaveLength(10);
    expect(routerReplace).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: englishAuth.recoveryCodes.download }));
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith(OBJECT_URL);

    const writeText = vi.spyOn(navigator.clipboard, "writeText");
    await user.click(screen.getByRole("button", { name: englishAuth.recoveryCodes.copy }));
    expect(writeText).toHaveBeenCalledWith(RECOVERY_CODES.join("\n"));

    const continueButton = screen.getByRole("button", {
      name: englishAuth.recoveryCodes.continue,
    });
    expect(continueButton).toBeDisabled();
    await user.click(screen.getByRole("checkbox", { name: englishAuth.recoveryCodes.saved }));
    expect(continueButton).toBeEnabled();

    await user.click(continueButton);
    expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
    expect(queryClient.getQueryData(["GET_CURRENT_USER_KEY"])).toBeUndefined();
    expect(countSetupCalls()).toBe(1);
  });

  it("shows an invalid confirm code inline", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor/setup": createSuccessResult({
        key: SETUP_KEY,
        setupUri: "otpauth://x",
      }),
      "/api/auth/two-factor/confirm": createErrorResult(401, "INVALID_TWO_FACTOR_CODE"),
    });
    renderWithProviders(<TwoFactorSetupPage />);

    await enterConfirmCode("000000");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishErrors.api.INVALID_TWO_FACTOR_CODE,
    );
  });

  it("goes to the two-factor step when setup is already done", async () => {
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor/setup": createErrorResult(409, "TWO_FACTOR_ALREADY_SET_UP"),
    });
    renderWithProviders(<TwoFactorSetupPage />);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/two-factor?next=%2Fprojects%2FSHOP%2Fruns");
    });
  });

  it("shows an error state with retry when setup cannot start", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      "/api/auth/two-factor/setup": createErrorResult(500, "CONFLICT"),
    });
    renderWithProviders(<TwoFactorSetupPage />);

    expect(await screen.findByText(englishAuth.twoFactorSetup.startFailed)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: englishAuth.twoFactorSetup.retry }));

    await waitFor(() => {
      expect(countSetupCalls()).toBe(2);
    });
  });

  it("redirects a signed-in session away without starting setup", async () => {
    respondWithRoutes(apiGet, {
      "/api/auth/me": createSuccessResult(createCurrentUser("signed_in")),
    });
    renderWithProviders(<TwoFactorSetupPage />);

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
    });
    expect(countSetupCalls()).toBe(0);
  });

  it("has no axe violations before and after the code is confirmed from the keyboard", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(<TwoFactorSetupPage />);

    const firstDigit = await screen.findByLabelText(
      `${englishAuth.twoFactorSetup.codeLabel}, digit 1 of 6`,
    );
    await screen.findByRole("img", { name: englishAuth.twoFactorSetup.qrCodeLabel });
    expect(await axe(container)).toHaveNoViolations();

    await tabTo(user, firstDigit);
    await user.keyboard("123456");

    await screen.findByRole("list", { name: englishAuth.recoveryCodes.listLabel });
    expect(await axe(container)).toHaveNoViolations();
    const savedCheckbox = screen.getByRole("checkbox", { name: englishAuth.recoveryCodes.saved });
    await tabTo(user, savedCheckbox);
    await user.keyboard(" ");
    const continueButton = screen.getByRole("button", {
      name: englishAuth.recoveryCodes.continue,
    });
    await tabTo(user, continueButton);
    await user.keyboard("{Enter}");

    expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP/runs");
  });
});
