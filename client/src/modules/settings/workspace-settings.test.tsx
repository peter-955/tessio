import {
  buildErrorResponse,
  buildSuccessResponse,
} from "@/components/project-context/test/utils/api-response.util";
import englishSettings from "@/lib/i18n/locales/en/settings.json";
import { apiGet, apiPut } from "@/modules/projects/test/mocks/api-client.mock";
import {
  buildValidationErrorResponse,
  respondWithRoutes,
} from "@/modules/projects/test/utils/api-routes.util";
import { renderWithContext } from "@/modules/projects/test/utils/render-with-context.util";
import { stubBrowserApis } from "@/modules/projects/test/utils/stub-browser-apis.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { WorkspaceSettingsPage } from "./workspace-settings";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("@/modules/projects/test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/projects/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const EMPTY_CONNECTION = {
  isConfigured: false,
  siteUrl: null,
  accountEmail: null,
  accountDisplayName: null,
  configuredAt: null,
};

const SAVED_CONNECTION = {
  isConfigured: true,
  siteUrl: "https://shop.atlassian.net",
  accountEmail: "jira@example.com",
  accountDisplayName: "Jira Bot",
  configuredAt: "2026-10-01T09:00:00Z",
};

const fillNewConnection = async (user: UserEvent): Promise<void> => {
  await user.type(
    await screen.findByRole("textbox", { name: /^Site URL/ }),
    "https://shop.atlassian.net",
  );
  await user.type(screen.getByRole("textbox", { name: /^Jira user email/ }), "jira@example.com");
};

const submitConnection = async (user: UserEvent): Promise<void> => {
  await user.click(screen.getByRole("button", { name: englishSettings.jira.submit }));
};

describe("WorkspaceSettingsPage", () => {
  beforeEach(() => {
    stubBrowserApis();
    apiGet.mockReset();
    apiPut.mockReset();
  });

  it("shows the admin-only state to members without calling the API", () => {
    renderWithContext(<WorkspaceSettingsPage />);

    expect(screen.getByText(englishSettings.adminOnly)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalled();
  });

  it("requires the API token on first setup", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/workspace/jira": buildSuccessResponse(EMPTY_CONNECTION) });
    const { container } = renderWithContext(<WorkspaceSettingsPage />, { workspaceRole: "admin" });

    expect(await screen.findByText(englishSettings.jira.notConnected)).toBeInTheDocument();
    await fillNewConnection(user);
    await submitConnection(user);

    expect(
      await screen.findByText(englishSettings.jira.errors.apiTokenRequired),
    ).toBeInTheDocument();
    expect(apiPut).not.toHaveBeenCalled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("keeps the saved token when the site URL is unchanged", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/workspace/jira": buildSuccessResponse(SAVED_CONNECTION) });
    respondWithRoutes(apiPut, { "/api/workspace/jira": buildSuccessResponse(SAVED_CONNECTION) });
    const { container } = renderWithContext(<WorkspaceSettingsPage />, { workspaceRole: "owner" });

    expect(await screen.findByText(englishSettings.jira.connected)).toBeInTheDocument();
    expect(
      screen.getByText(/as Jira Bot \(jira@example\.com\) on https:\/\/shop\.atlassian\.net since/),
    ).toBeInTheDocument();
    expect(screen.getByText(englishSettings.jira.apiTokenKeep)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: englishSettings.jira.apiTokenHelp })).toHaveAttribute(
      "href",
      "https://id.atlassian.com/manage-profile/security/api-tokens",
    );
    await submitConnection(user);

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/workspace/jira", {
        body: {
          siteUrl: "https://shop.atlassian.net",
          accountEmail: "jira@example.com",
          apiToken: null,
        },
      });
    });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the invalid credentials alert", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/workspace/jira": buildSuccessResponse(SAVED_CONNECTION) });
    respondWithRoutes(apiPut, {
      "/api/workspace/jira": buildErrorResponse(422, "JIRA_INVALID_CREDENTIALS"),
    });
    renderWithContext(<WorkspaceSettingsPage />, { workspaceRole: "admin" });

    await screen.findByText(englishSettings.jira.connected);
    await submitConnection(user);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      englishSettings.jira.errors.invalidCredentials,
    );
  });

  it("maps an invalid email from the server to its field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/workspace/jira": buildSuccessResponse(SAVED_CONNECTION) });
    respondWithRoutes(apiPut, {
      "/api/workspace/jira": buildValidationErrorResponse("accountEmail"),
    });
    renderWithContext(<WorkspaceSettingsPage />, { workspaceRole: "admin" });

    await screen.findByText(englishSettings.jira.connected);
    await submitConnection(user);

    expect(await screen.findByText(englishSettings.jira.errors.invalidRequest)).toBeInTheDocument();
    expect(screen.getByText(englishSettings.jira.errors.emailInvalid)).toBeInTheDocument();
  });

  it("clears the token after a successful save", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/workspace/jira": buildSuccessResponse(EMPTY_CONNECTION) });
    respondWithRoutes(apiPut, { "/api/workspace/jira": buildSuccessResponse(SAVED_CONNECTION) });
    renderWithContext(<WorkspaceSettingsPage />, { workspaceRole: "admin" });

    await fillNewConnection(user);
    const tokenInput = screen.getByLabelText(/^API token/);
    await user.type(tokenInput, "secret-token");
    await submitConnection(user);

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/workspace/jira", {
        body: {
          siteUrl: "https://shop.atlassian.net",
          accountEmail: "jira@example.com",
          apiToken: "secret-token",
        },
      });
    });
    expect((await screen.findAllByText("Jira connected as Jira Bot"))[0]).toBeInTheDocument();
    await waitFor(() => {
      expect(tokenInput).toHaveValue("");
    });
    expect(screen.getByText(englishSettings.jira.connected)).toBeInTheDocument();
  });
});
