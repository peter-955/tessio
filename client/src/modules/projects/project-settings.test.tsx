import { buildSuccessResponse } from "@/components/project-context/test/utils/api-response.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
  VIEWER_CAPABILITIES,
} from "@/components/project-context/test/utils/project-fixture.util";
import type { Project } from "@/components/project-context/typing/types/project.type";
import englishLabels from "@/lib/i18n/locales/en/labels.json";
import englishProjects from "@/lib/i18n/locales/en/projects.json";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ProjectSettingsPage } from "./project-settings";
import { apiGet, apiPatch } from "./test/mocks/api-client.mock";
import { respondWithRoutes } from "./test/utils/api-routes.util";
import { chooseOption } from "./test/utils/choose-option.util";
import { renderWithContext } from "./test/utils/render-with-context.util";
import { stubBrowserApis } from "./test/utils/stub-browser-apis.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const STAGING_ID = "3f2e1d0c-9b8a-4c7d-8e6f-5a4b3c2d1e0f";

const editableProject = buildProject({
  myRole: "admin",
  capabilities: ADMIN_CAPABILITIES,
  allowedFileTypes: ["image/png", "application/pdf"],
  defaultEnvironmentId: STAGING_ID,
});

const respondWithOptions = (): void => {
  respondWithRoutes(apiGet, {
    "/api/workspace/jira/boards": buildSuccessResponse([
      { id: 1, name: "Shop board", type: "scrum" },
      { id: 2, name: "Ops board", type: "kanban" },
    ]),
    "/api/projects/{project_key}/environments": buildSuccessResponse([
      {
        id: STAGING_ID,
        name: "Staging",
        baseUrl: "https://staging.example.com",
        healthCheckUrl: null,
        isArchived: false,
        archivedAt: null,
        createdAt: "2026-10-01T09:00:00Z",
      },
    ]),
    "/api/projects/{project_key}/labels": buildSuccessResponse([]),
  });
};

const respondToPatch = (): void => {
  respondWithRoutes(apiPatch, {
    "/api/projects/{project_key}": (options) => {
      const { body } = options as { body: Partial<Project> };
      return buildSuccessResponse({ ...editableProject, ...body });
    },
  });
};

const findCard = async (title: string): Promise<HTMLElement> => {
  const heading = await screen.findByRole("heading", { name: title });
  const card = heading.parentElement;
  if (card === null) {
    throw new Error(`No card for ${title}`);
  }

  return card;
};

describe("ProjectSettingsPage", () => {
  beforeEach(() => {
    stubBrowserApis();
    apiGet.mockReset();
    apiPatch.mockReset();
    respondWithOptions();
    respondToPatch();
  });

  it("patches only the changed general fields", async () => {
    const user = userEvent.setup();
    const { container, queryClient } = renderWithContext(<ProjectSettingsPage />, {
      project: editableProject,
      workspaceRole: "admin",
    });
    const card = await findCard(englishProjects.settings.general.title);
    const saveButton = within(card).getByRole("button", { name: englishProjects.settings.save });
    expect(saveButton).toBeDisabled();

    const nameInput = within(card).getByRole("textbox", { name: /^Name/ });
    await user.clear(nameInput);
    await user.type(nameInput, "Shop EU");
    await user.click(saveButton);

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith("/api/projects/{project_key}", {
        params: { path: { project_key: "SHOP" } },
        body: { name: "Shop EU" },
      });
    });
    expect(await screen.findByText(englishProjects.settings.saved)).toBeInTheDocument();
    expect(queryClient.getQueryData<Project>([GET_PROJECT_KEY, "SHOP"])?.name).toBe("Shop EU");
    await waitFor(() => {
      expect(saveButton).toBeDisabled();
    });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("sends null when the default environment is cleared", async () => {
    const user = userEvent.setup();
    renderWithContext(<ProjectSettingsPage />, { project: editableProject });
    const card = await findCard(englishProjects.settings.defaults.title);
    const environmentSelect = await within(card).findByRole("combobox", {
      name: /^Default environment/,
    });
    await waitFor(() => {
      expect(environmentSelect).toHaveValue("Staging");
    });

    await chooseOption(user, environmentSelect, "Staging");
    await user.click(within(card).getByRole("button", { name: englishProjects.settings.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith("/api/projects/{project_key}", {
        params: { path: { project_key: "SHOP" } },
        body: { defaultEnvironmentId: null },
      });
    });
  });

  it("rejects an invalid MIME type and adds a valid one", async () => {
    const user = userEvent.setup();
    renderWithContext(<ProjectSettingsPage />, { project: editableProject });
    const card = await findCard(englishProjects.settings.fileTypes.title);
    const otherTypeInput = within(card).getByRole("textbox", {
      name: englishProjects.settings.fileTypes.otherType,
    });
    const addButton = within(card).getByRole("button", {
      name: englishProjects.settings.fileTypes.add,
    });

    await user.type(otherTypeInput, "markdown");
    await user.click(addButton);
    expect(
      await within(card).findByText(englishProjects.settings.fileTypes.invalidType),
    ).toBeInTheDocument();

    await user.clear(otherTypeInput);
    await user.type(otherTypeInput, "Text/X-Custom");
    await user.click(addButton);
    expect(otherTypeInput).toHaveValue("");
    await user.click(within(card).getByRole("button", { name: englishProjects.settings.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith("/api/projects/{project_key}", {
        params: { path: { project_key: "SHOP" } },
        body: { allowedFileTypes: ["image/png", "application/pdf", "text/x-custom"] },
      });
    });
  });

  it("blocks saving without any file type", async () => {
    const user = userEvent.setup();
    renderWithContext(<ProjectSettingsPage />, {
      project: { ...editableProject, allowedFileTypes: ["image/png"] },
    });
    const card = await findCard(englishProjects.settings.fileTypes.title);

    await user.click(within(card).getByLabelText(/^File types/));
    await user.keyboard("{Backspace}");
    await user.click(within(card).getByRole("button", { name: englishProjects.settings.save }));

    expect(
      await within(card).findByText(englishProjects.settings.fileTypes.atLeastOne),
    ).toBeInTheDocument();
    expect(apiPatch).not.toHaveBeenCalled();
  });

  it("shows the archive card to workspace admins only", async () => {
    const { unmount } = renderWithContext(<ProjectSettingsPage />, {
      project: editableProject,
      workspaceRole: "owner",
    });

    expect(
      await screen.findByRole("button", { name: englishProjects.settings.archive.action }),
    ).toBeInTheDocument();
    unmount();

    renderWithContext(<ProjectSettingsPage />, { project: editableProject });
    expect(await screen.findByText(englishProjects.settings.general.title)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: englishProjects.settings.archive.action }),
    ).not.toBeInTheDocument();
  });

  it("shows the label manager card after the allowed file types card", async () => {
    renderWithContext(<ProjectSettingsPage />, { project: editableProject });

    const labelsCard = await findCard(englishLabels.manager.title);
    const fileTypesCard = await findCard(englishProjects.settings.fileTypes.title);
    expect(await within(labelsCard).findByText(englishLabels.manager.empty)).toBeInTheDocument();
    expect(
      fileTypesCard.compareDocumentPosition(labelsCard) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it("shows the read-only notice on an archived project", async () => {
    const archivedProject = buildProject({
      isArchived: true,
      archivedAt: "2026-10-20T09:00:00Z",
      capabilities: VIEWER_CAPABILITIES,
    });
    const { container } = renderWithContext(<ProjectSettingsPage />, {
      project: archivedProject,
      workspaceRole: "admin",
    });

    expect(screen.getByText(englishProjects.settings.readOnlyArchived)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: englishProjects.list.actions.unarchive }),
    ).toBeInTheDocument();
    expect(screen.queryByText(englishProjects.settings.general.title)).not.toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("asks members without the edit capability for the project Admin role", () => {
    renderWithContext(<ProjectSettingsPage />, { project: buildProject() });

    expect(screen.getByText(englishProjects.settings.needsAdmin)).toBeInTheDocument();
  });
});
