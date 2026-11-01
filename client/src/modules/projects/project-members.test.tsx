import {
  buildErrorResponse,
  buildSuccessResponse,
} from "@/components/project-context/test/utils/api-response.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import englishErrors from "@/lib/i18n/locales/en/errors.json";
import englishProjects from "@/lib/i18n/locales/en/projects.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ProjectMembersPage } from "./project-members";
import { apiDelete, apiGet, apiPut } from "./test/mocks/api-client.mock";
import { routerPush } from "./test/mocks/next-navigation.mock";
import { buildNoContentResponse, respondWithRoutes } from "./test/utils/api-routes.util";
import { chooseOption } from "./test/utils/choose-option.util";
import { CURRENT_USER_ID } from "./test/utils/current-user.fixture";
import { renderWithContext } from "./test/utils/render-with-context.util";
import { stubBrowserApis } from "./test/utils/stub-browser-apis.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const ADA_ID = "5a3b0d7e-1c2f-4e8a-9b6d-7f0e1a2b3c4d";

const ADA: ProjectMember = {
  userId: ADA_ID,
  name: "Ada Lovelace",
  email: "ada@example.com",
  userStatus: "active",
  role: "admin",
  addedAt: "2026-10-01T09:00:00Z",
};

const LAN: ProjectMember = {
  userId: CURRENT_USER_ID,
  name: "Lan Nguyen",
  email: "lan@example.com",
  userStatus: "invited",
  role: "qc",
  addedAt: "2026-10-02T09:00:00Z",
};

const adminProject = buildProject({ myRole: "admin", capabilities: ADMIN_CAPABILITIES });

const respondWithMembers = (): void => {
  respondWithRoutes(apiGet, {
    "/api/projects/{project_key}/members": buildSuccessResponse([ADA, LAN]),
    "/api/projects/{project_key}/members/candidates": buildSuccessResponse([
      {
        userId: "9d8c7b6a-5f4e-4d3c-8b2a-1f0e9d8c7b6a",
        name: "Bao Tran",
        email: "bao@example.com",
        userStatus: "invited",
      },
    ]),
  });
};

describe("ProjectMembersPage", () => {
  beforeEach(() => {
    stubBrowserApis();
    apiGet.mockReset();
    apiPut.mockReset();
    apiDelete.mockReset();
    routerPush.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows a read-only list to viewers", async () => {
    respondWithMembers();
    const { container } = renderWithContext(<ProjectMembersPage />, { project: buildProject() });

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    expect(screen.getByText(englishProjects.members.invited)).toBeInTheDocument();
    expect(screen.getByText(englishProjects.roles.admin)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: englishProjects.members.add }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Remove Ada Lovelace" })).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("puts the new role when an admin changes it", async () => {
    const user = userEvent.setup();
    respondWithMembers();
    respondWithRoutes(apiPut, {
      "/api/projects/{project_key}/members/{user_id}": buildSuccessResponse({
        ...ADA,
        role: "dev",
      }),
    });
    const { container } = renderWithContext(<ProjectMembersPage />, {
      project: adminProject,
      workspaceRole: "admin",
    });

    await chooseOption(
      user,
      await screen.findByRole("combobox", { name: "Role for Ada Lovelace" }),
      englishProjects.roles.dev,
    );

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/projects/{project_key}/members/{user_id}", {
        params: { path: { project_key: "SHOP", user_id: ADA_ID } },
        body: { role: "dev" },
      });
    });
    expect(await screen.findByText(englishProjects.members.roleUpdated)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the last admin error and keeps the saved role", async () => {
    const user = userEvent.setup();
    respondWithMembers();
    respondWithRoutes(apiPut, {
      "/api/projects/{project_key}/members/{user_id}": buildErrorResponse(
        409,
        "LAST_PROJECT_ADMIN",
      ),
    });
    renderWithContext(<ProjectMembersPage />, { project: adminProject });

    const roleSelect = await screen.findByRole("combobox", { name: "Role for Ada Lovelace" });
    await chooseOption(user, roleSelect, englishProjects.roles.viewer);

    expect(await screen.findByText(englishErrors.api.LAST_PROJECT_ADMIN)).toBeInTheDocument();
    await waitFor(() => {
      expect(roleSelect).toHaveValue(englishProjects.roles.admin);
    });
  });

  it("searches candidates with the debounced query and adds the chosen user", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    respondWithMembers();
    respondWithRoutes(apiPut, {
      "/api/projects/{project_key}/members/{user_id}": buildSuccessResponse(LAN),
    });
    renderWithContext(<ProjectMembersPage />, { project: adminProject });

    await user.click(await screen.findByRole("button", { name: englishProjects.members.add }));
    const dialog = await screen.findByRole("dialog", { name: englishProjects.addMember.title });
    await user.type(
      within(dialog).getByRole("textbox", { name: englishProjects.addMember.search }),
      "bao",
    );
    await vi.advanceTimersByTimeAsync(300);

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith("/api/projects/{project_key}/members/candidates", {
        params: { path: { project_key: "SHOP" }, query: { query: "bao" } },
      });
    });
    expect(apiGet).not.toHaveBeenCalledWith("/api/projects/{project_key}/members/candidates", {
      params: { path: { project_key: "SHOP" }, query: { query: "b" } },
    });

    await chooseOption(
      user,
      within(dialog).getByRole("combobox", { name: /^User/ }),
      "Bao Tran · bao@example.com (invited)",
    );
    await chooseOption(
      user,
      within(dialog).getByRole("combobox", { name: /^Role/ }),
      englishProjects.roles.ba,
    );
    await user.click(
      within(dialog).getByRole("button", { name: englishProjects.addMember.submit }),
    );

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith("/api/projects/{project_key}/members/{user_id}", {
        params: { path: { project_key: "SHOP", user_id: "9d8c7b6a-5f4e-4d3c-8b2a-1f0e9d8c7b6a" } },
        body: { role: "ba" },
      });
    });
    expect(await screen.findByText(englishProjects.members.memberAdded)).toBeInTheDocument();
  });

  it("leaves the project after removing yourself", async () => {
    const user = userEvent.setup();
    respondWithMembers();
    respondWithRoutes(apiDelete, {
      "/api/projects/{project_key}/members/{user_id}": buildNoContentResponse(),
    });
    renderWithContext(<ProjectMembersPage />, { project: adminProject });

    await user.click(await screen.findByRole("button", { name: "Remove Lan Nguyen" }));
    const dialog = await screen.findByRole("dialog", { name: "Remove Lan Nguyen?" });
    expect(within(dialog).getByText(englishProjects.members.removeSelf)).toBeInTheDocument();
    await user.click(
      within(dialog).getByRole("button", { name: englishProjects.members.removeConfirm }),
    );

    await waitFor(() => {
      expect(apiDelete).toHaveBeenCalledWith("/api/projects/{project_key}/members/{user_id}", {
        params: { path: { project_key: "SHOP", user_id: CURRENT_USER_ID } },
      });
    });
    await waitFor(() => {
      expect(routerPush).toHaveBeenCalledWith("/projects");
    });
  });
});
