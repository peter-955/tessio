import {
  buildErrorResponse,
  buildSuccessResponse,
} from "@/components/project-context/test/utils/api-response.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import englishProjects from "@/lib/i18n/locales/en/projects.json";
import { GET_PROJECT_KEY } from "@/shared/hooks/queries/use-get-project";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ProjectsPage } from "./projects";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { respondWithRoutes } from "./test/utils/api-routes.util";
import { renderWithContext } from "./test/utils/render-with-context.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const shopProject = buildProject({
  description: "Storefront and checkout",
  myRole: "admin",
  capabilities: ADMIN_CAPABILITIES,
});

describe("ProjectsPage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
  });

  it("lets a workspace admin create and archive projects", async () => {
    const user = userEvent.setup();
    const archivedProject = { ...shopProject, isArchived: true, capabilities: [] };
    respondWithRoutes(apiGet, { "/api/projects": buildSuccessResponse([shopProject]) });
    respondWithRoutes(apiPost, {
      "/api/projects/{project_key}/archive": buildSuccessResponse(archivedProject),
    });
    const { container, queryClient } = renderWithContext(<ProjectsPage />, {
      workspaceRole: "admin",
    });

    const row = (await screen.findByRole("link", { name: "Shop" })).closest("tr");
    expect(row).not.toBeNull();
    expect(
      screen.getAllByRole("link", { name: englishProjects.list.newProject })[0],
    ).toHaveAttribute("href", "/projects/new");
    expect(screen.getByText("Storefront and checkout")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();

    await user.click(within(row as HTMLElement).getByRole("button", { name: "Actions for Shop" }));
    expect(
      await screen.findByRole("menuitem", {
        name: englishProjects.list.actions.members,
        hidden: true,
      }),
    ).toHaveAttribute("href", "/projects/SHOP/members");
    expect(
      await screen.findByRole("menuitem", {
        name: englishProjects.list.actions.settings,
        hidden: true,
      }),
    ).toHaveAttribute("href", "/projects/SHOP/settings");
    await user.click(
      await screen.findByRole("menuitem", {
        name: englishProjects.list.actions.archive,
        hidden: true,
      }),
    );
    const dialog = await screen.findByRole("dialog", { name: "Archive Shop?" });
    await user.click(within(dialog).getByRole("button", { name: englishProjects.archive.confirm }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith("/api/projects/{project_key}/archive", {
        params: { path: { project_key: "SHOP" } },
      });
    });
    expect(await screen.findByText(englishProjects.archive.success)).toBeInTheDocument();
    expect(queryClient.getQueryData([GET_PROJECT_KEY, "SHOP"])).toEqual(archivedProject);
  });

  it("hides admin actions from members and shows the member empty state", async () => {
    respondWithRoutes(apiGet, { "/api/projects": buildSuccessResponse([]) });
    const { container } = renderWithContext(<ProjectsPage />);

    expect(await screen.findByText(englishProjects.list.empty.memberTitle)).toBeInTheDocument();
    expect(screen.getByText(englishProjects.list.empty.memberDescription)).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: englishProjects.list.newProject }),
    ).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows no archive action to members", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, {
      "/api/projects": buildSuccessResponse([buildProject({ myRole: "qc" })]),
    });
    renderWithContext(<ProjectsPage />);

    await user.click(await screen.findByRole("button", { name: "Actions for Shop" }));

    expect(
      await screen.findByRole("menuitem", {
        name: englishProjects.list.actions.members,
        hidden: true,
      }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("menuitem", { name: englishProjects.list.actions.archive, hidden: true }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("menuitem", { name: englishProjects.list.actions.settings, hidden: true }),
    ).not.toBeInTheDocument();
  });

  it("requests the archived projects when the switch is on", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiGet, { "/api/projects": buildSuccessResponse([shopProject]) });
    renderWithContext(<ProjectsPage />, { workspaceRole: "admin" });

    await user.click(
      await screen.findByRole("switch", { name: englishProjects.list.showArchived }),
    );

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith("/api/projects", {
        params: { query: { includeArchived: true } },
      });
    });
  });

  it("shows an error state with retry", async () => {
    respondWithRoutes(apiGet, { "/api/projects": buildErrorResponse(500, "CONFLICT") });
    renderWithContext(<ProjectsPage />);

    expect(await screen.findByText(englishProjects.list.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishProjects.errors.retry })).toBeInTheDocument();
  });
});
