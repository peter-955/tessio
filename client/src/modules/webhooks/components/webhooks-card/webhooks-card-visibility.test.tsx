import {
  ADMIN_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import englishIntegrations from "@/lib/i18n/locales/en/integrations.json";
import englishProjects from "@/lib/i18n/locales/en/projects.json";
import { createSuccessResult, respondWithRoutes } from "@/modules/auth/test/utils/api-result.util";
import { ProjectSettingsPage } from "@/modules/projects/project-settings";
import { renderWithContext } from "@/modules/projects/test/utils/render-with-context.util";
import { stubBrowserApis } from "@/modules/projects/test/utils/stub-browser-apis.util";
import { screen } from "@testing-library/react";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { apiGet } from "../../test/mocks/api-client.mock";
import { buildIntegrationAdminProject, buildWebhook } from "../../test/utils/webhook.fixture";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/projects/test/mocks/next-navigation.mock")).nextNavigationMock;
});

describe("Webhooks in project settings", () => {
  beforeAll(() => {
    stubBrowserApis();
  });

  beforeEach(() => {
    apiGet.mockReset();
    respondWithRoutes(apiGet, {
      "/api/workspace/jira/boards": createSuccessResult([]),
      "/api/projects/{project_key}/environments": createSuccessResult([]),
      "/api/projects/{project_key}/labels": createSuccessResult([]),
      "/api/projects/{project_key}/chat-channels": createSuccessResult([]),
      "/api/projects/{project_key}/webhooks": createSuccessResult([buildWebhook()]),
    });
  });

  it("shows the webhooks card to a project Admin with integration.manage", async () => {
    renderWithContext(<ProjectSettingsPage />, { project: buildIntegrationAdminProject() });

    expect(
      await screen.findByRole("heading", { name: englishIntegrations.webhooks.title }),
    ).toBeInTheDocument();
    expect(await screen.findByText(buildWebhook().url)).toBeInTheDocument();
  });

  it("hides the webhooks card without integration.manage", async () => {
    renderWithContext(<ProjectSettingsPage />, {
      project: buildProject({ myRole: "admin", capabilities: ADMIN_CAPABILITIES }),
    });

    expect(
      await screen.findByRole("heading", { name: englishProjects.settings.general.title }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: englishIntegrations.webhooks.title }),
    ).not.toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalledWith(
      "/api/projects/{project_key}/webhooks",
      expect.anything(),
    );
  });

  it("hides the webhooks card on an archived project", async () => {
    renderWithContext(<ProjectSettingsPage />, {
      project: buildIntegrationAdminProject({
        isArchived: true,
        archivedAt: "2026-11-01T09:00:00Z",
      }),
    });

    expect(
      await screen.findByRole("heading", { name: englishProjects.settings.general.title }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: englishIntegrations.webhooks.title }),
    ).not.toBeInTheDocument();
  });
});
