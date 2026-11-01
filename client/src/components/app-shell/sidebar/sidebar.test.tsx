import {
  buildErrorResponse,
  buildSuccessResponse,
  type ApiResponseStub,
} from "@/components/project-context/test/utils/api-response.util";
import {
  ADMIN_CAPABILITIES,
  buildProject,
  VIEWER_CAPABILITIES,
} from "@/components/project-context/test/utils/project-fixture.util";
import {
  readLastProjectKey,
  storeLastProjectKey,
} from "@/components/project-context/utils/last-project-key.util";
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import type { WorkspaceRole } from "../typing/types/workspace-role.type";
import { Sidebar } from "./sidebar";

const { getRequest, navigation, session } = vi.hoisted(() => {
  return {
    getRequest: vi.fn<(path: string, options?: unknown) => Promise<ApiResponseStub>>(),
    navigation: { pathname: "/", params: {} as Record<string, string> },
    session: { workspaceRole: "member" as WorkspaceRole },
  };
});

vi.mock("@/lib/api/api-client", () => {
  return { apiClient: { GET: getRequest, POST: vi.fn() } };
});

vi.mock("next/navigation", () => {
  return {
    usePathname: () => {
      return navigation.pathname;
    },
    useParams: () => {
      return navigation.params;
    },
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

vi.mock("@/components/session-guard/hooks/use-current-user", () => {
  return {
    useCurrentUser: () => {
      return {
        id: "0b7f4a8e-3c55-4f5e-8f3e-2a0c9f1d6b21",
        email: "lan@example.com",
        name: "Lan Nguyen",
        workspaceRole: session.workspaceRole,
        nextStep: "signed_in",
      };
    },
  };
});

const visitProjectPage = (pathname: string): void => {
  navigation.pathname = pathname;
  navigation.params = { projectKey: "SHOP" };
};

const renderSidebar = (): ReturnType<typeof render> => {
  return render(
    <TestProviders queryClient={createTestQueryClient()}>
      <Sidebar />
    </TestProviders>,
  );
};

const findProjectNavigation = async (): Promise<HTMLElement> => {
  return screen.findByRole("navigation", { name: "Project navigation" });
};

beforeEach(() => {
  navigation.pathname = "/";
  navigation.params = {};
  session.workspaceRole = "member";
});

afterEach(() => {
  window.localStorage.clear();
});

describe("Sidebar", () => {
  it("links every project item under the project key and hides Settings from a viewer", async () => {
    visitProjectPage("/projects/SHOP/runs/42");
    getRequest.mockResolvedValue(
      buildSuccessResponse(buildProject({ capabilities: VIEWER_CAPABILITIES })),
    );

    const { container } = renderSidebar();
    const projectNavigation = await findProjectNavigation();

    expect(within(projectNavigation).getByText("Shop")).toBeInTheDocument();
    expect(within(projectNavigation).getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      "/projects/SHOP",
    );
    expect(within(projectNavigation).getByRole("link", { name: "Runs" })).toHaveAttribute(
      "href",
      "/projects/SHOP/runs",
    );
    expect(within(projectNavigation).getByRole("link", { name: "Members" })).toHaveAttribute(
      "href",
      "/projects/SHOP/members",
    );
    expect(
      within(projectNavigation).queryByRole("link", { name: "Settings" }),
    ).not.toBeInTheDocument();
    expect(getRequest).toHaveBeenCalledWith("/api/projects/{project_key}", {
      params: { path: { project_key: "SHOP" } },
    });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows Settings to a project admin", async () => {
    visitProjectPage("/projects/SHOP/settings");
    getRequest.mockResolvedValue(
      buildSuccessResponse(buildProject({ myRole: "admin", capabilities: ADMIN_CAPABILITIES })),
    );

    renderSidebar();
    const projectNavigation = await findProjectNavigation();

    expect(within(projectNavigation).getByRole("link", { name: "Settings" })).toHaveAttribute(
      "href",
      "/projects/SHOP/settings",
    );
  });

  it("marks the active item, matching the dashboard exactly", async () => {
    visitProjectPage("/projects/SHOP/runs/42");
    getRequest.mockResolvedValue(buildSuccessResponse(buildProject()));

    renderSidebar();
    const projectNavigation = await findProjectNavigation();

    expect(within(projectNavigation).getByRole("link", { name: "Runs" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(within(projectNavigation).getByRole("link", { name: "Dashboard" })).not.toHaveAttribute(
      "aria-current",
    );
    expect(screen.getByRole("link", { name: "Projects" })).not.toHaveAttribute("aria-current");
  });

  it("marks the dashboard on the project overview", async () => {
    visitProjectPage("/projects/SHOP");
    getRequest.mockResolvedValue(buildSuccessResponse(buildProject()));

    renderSidebar();
    const projectNavigation = await findProjectNavigation();

    expect(within(projectNavigation).getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("uses the last project outside a project route", async () => {
    storeLastProjectKey("SHOP");
    getRequest.mockResolvedValue(buildSuccessResponse(buildProject()));

    renderSidebar();
    const projectNavigation = await findProjectNavigation();

    expect(within(projectNavigation).getByRole("link", { name: "Runs" })).toHaveAttribute(
      "href",
      "/projects/SHOP/runs",
    );
  });

  it("shows the no-project hint without an active project", async () => {
    navigation.pathname = "/projects";

    const { container } = renderSidebar();

    expect(
      screen.getByText("Pick a project to see its sprints, stories and runs."),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "All projects" })).toHaveAttribute("href", "/projects");
    expect(
      screen.queryByRole("navigation", { name: "Project navigation" }),
    ).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Projects" })).toHaveAttribute("aria-current", "page");
    expect(getRequest).not.toHaveBeenCalled();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("forgets the last project and shows the hint when it no longer exists", async () => {
    storeLastProjectKey("GONE");
    getRequest.mockResolvedValue(buildErrorResponse(404, "NOT_FOUND"));

    renderSidebar();

    expect(
      await screen.findByText("Pick a project to see its sprints, stories and runs."),
    ).toBeInTheDocument();
    expect(readLastProjectKey()).toBeNull();
  });

  it("hides admin-only workspace items from a member", () => {
    renderSidebar();

    expect(screen.queryByRole("link", { name: "Users" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Workspace settings" })).not.toBeInTheDocument();
  });

  it("shows admin-only workspace items to a workspace admin", () => {
    session.workspaceRole = "admin";

    renderSidebar();

    expect(screen.getByRole("link", { name: "Users" })).toHaveAttribute("href", "/users");
    expect(screen.getByRole("link", { name: "Workspace settings" })).toHaveAttribute(
      "href",
      "/settings",
    );
  });

  it("shows the workspace navigation without the language and theme controls", () => {
    renderSidebar();

    const workspaceNavigation = screen.getByRole("navigation", { name: "Workspace navigation" });

    expect(within(workspaceNavigation).getByRole("link", { name: "Projects" })).toHaveAttribute(
      "href",
      "/projects",
    );
    expect(screen.queryByRole("radiogroup", { name: "Language" })).not.toBeInTheDocument();
    expect(screen.queryByRole("radiogroup", { name: "Color theme" })).not.toBeInTheDocument();
  });

  it("calls onNavigate when a link is chosen", async () => {
    const handleNavigate = vi.fn<() => void>();
    render(
      <TestProviders queryClient={createTestQueryClient()}>
        <Sidebar onNavigate={handleNavigate} />
      </TestProviders>,
    );

    screen.getByRole("link", { name: "Projects" }).click();

    expect(handleNavigate).toHaveBeenCalledTimes(1);
  });
});
