import {
  buildErrorResponse,
  buildSuccessResponse,
} from "@/components/project-context/test/utils/api-response.util";
import { buildProject } from "@/components/project-context/test/utils/project-fixture.util";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishProjects from "@/lib/i18n/locales/en/projects.json";
import { screen, waitFor } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { NewProjectPage } from "./new-project";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerPush } from "./test/mocks/next-navigation.mock";
import { respondWithRoutes } from "./test/utils/api-routes.util";
import { renderWithContext } from "./test/utils/render-with-context.util";
import { stubBrowserApis } from "./test/utils/stub-browser-apis.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const CONFIGURED_CONNECTION = {
  isConfigured: true,
  siteUrl: "https://shop.atlassian.net",
  accountEmail: "jira@example.com",
  accountDisplayName: "Jira Bot",
  configuredAt: "2026-10-01T09:00:00Z",
};

const JIRA_PROJECTS = [
  { id: "10000", key: "SHOP", name: "Shop" },
  { id: "10001", key: "DOCS", name: "Docs" },
];

const JIRA_BOARDS = [{ id: 7, name: "Shop board", type: "scrum" }];

const respondWithJira = (): void => {
  respondWithRoutes(apiGet, {
    "/api/workspace/jira": buildSuccessResponse(CONFIGURED_CONNECTION),
    "/api/workspace/jira/projects": buildSuccessResponse(JIRA_PROJECTS),
    "/api/workspace/jira/boards": buildSuccessResponse(JIRA_BOARDS),
  });
};

const chooseJiraProject = async (user: UserEvent): Promise<void> => {
  await user.click(await screen.findByRole("combobox", { name: /^Jira project/ }));
  await user.click(await screen.findByRole("option", { name: "SHOP · Shop", hidden: true }));
};

const submitForm = async (user: UserEvent): Promise<void> => {
  await user.click(screen.getByRole("button", { name: englishProjects.create.submit }));
};

describe("NewProjectPage", () => {
  beforeEach(() => {
    stubBrowserApis();
    apiGet.mockReset();
    apiPost.mockReset();
    routerPush.mockReset();
  });

  it("shows the admin-only state to members without calling the API", () => {
    renderWithContext(<NewProjectPage />);

    expect(screen.getByText(englishProjects.create.adminOnly)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalled();
  });

  it("links to the Jira settings when Jira is not configured", async () => {
    respondWithRoutes(apiGet, {
      "/api/workspace/jira": buildSuccessResponse({
        isConfigured: false,
        siteUrl: null,
        accountEmail: null,
        accountDisplayName: null,
        configuredAt: null,
      }),
    });
    const { container } = renderWithContext(<NewProjectPage />, { workspaceRole: "admin" });

    expect(
      await screen.findByRole("link", { name: englishProjects.create.jiraRequired.action }),
    ).toHaveAttribute("href", "/settings");
    expect(apiGet).not.toHaveBeenCalledWith("/api/workspace/jira/projects");
    expect(await axe(container)).toHaveNoViolations();
  });

  it("loads the boards and prefills the key, the name and the single board", async () => {
    const user = userEvent.setup();
    respondWithJira();
    const { container } = renderWithContext(<NewProjectPage />, { workspaceRole: "owner" });

    await chooseJiraProject(user);

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith("/api/workspace/jira/boards", {
        params: { query: { jiraProjectKey: "SHOP" } },
      });
    });
    expect(screen.getByRole("textbox", { name: /^Key/ })).toHaveValue("SHOP");
    expect(screen.getByRole("textbox", { name: /^Name/ })).toHaveValue("Shop");
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Jira board/ })).toHaveValue(
        "Shop board (scrum)",
      );
    });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("posts the exact request and opens the members page", async () => {
    const user = userEvent.setup();
    respondWithJira();
    respondWithRoutes(apiPost, {
      "/api/projects": buildSuccessResponse(buildProject({ key: "SHOP" })),
    });
    renderWithContext(<NewProjectPage />, { workspaceRole: "admin" });

    await chooseJiraProject(user);
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Jira board/ })).toHaveValue(
        "Shop board (scrum)",
      );
    });
    await user.type(screen.getByRole("textbox", { name: /^Description/ }), "  Storefront  ");
    await submitForm(user);

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/projects", {
        body: {
          key: "SHOP",
          name: "Shop",
          description: "Storefront",
          jiraProjectKey: "SHOP",
          jiraBoardId: 7,
        },
      });
    });
    await waitFor(() => {
      expect(routerPush).toHaveBeenCalledWith("/projects/SHOP/members");
    });
  });

  it("shows a used key on the key field", async () => {
    const user = userEvent.setup();
    respondWithJira();
    respondWithRoutes(apiPost, {
      "/api/projects": buildErrorResponse(409, "PROJECT_KEY_ALREADY_USED"),
    });
    renderWithContext(<NewProjectPage />, { workspaceRole: "admin" });

    await chooseJiraProject(user);
    await waitFor(() => {
      expect(screen.getByRole("combobox", { name: /^Jira board/ })).toHaveValue(
        "Shop board (scrum)",
      );
    });
    await submitForm(user);

    expect(await screen.findByText(englishErrors.api.PROJECT_KEY_ALREADY_USED)).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: /^Key/ })).toHaveAttribute("aria-invalid", "true");
    expect(routerPush).not.toHaveBeenCalled();
  });

  it("blocks the submit when the key is invalid", async () => {
    const user = userEvent.setup();
    respondWithJira();
    renderWithContext(<NewProjectPage />, { workspaceRole: "admin" });

    await chooseJiraProject(user);
    const keyInput = screen.getByRole("textbox", { name: /^Key/ });
    await user.clear(keyInput);
    await user.type(keyInput, "9-a");
    expect(keyInput).toHaveValue("9A");
    await submitForm(user);

    expect(await screen.findByText(englishProjects.errors.keyInvalid)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();
  });
});
