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
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { ProjectSwitcher } from "./project-switcher";

const { getRequest, navigation } = vi.hoisted(() => {
  return {
    getRequest: vi.fn<(path: string, options?: unknown) => Promise<ApiResponseStub>>(),
    navigation: { pathname: "/", params: {} as Record<string, string> },
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

const shopProject = buildProject({ capabilities: ADMIN_CAPABILITIES, myRole: "admin" });
const docsProject = buildProject({
  id: "a3b2c1d0-1111-4222-8333-444455556666",
  key: "DOCS",
  name: "Docs",
  capabilities: VIEWER_CAPABILITIES,
});
const blogProject = buildProject({
  id: "b4c3d2e1-1111-4222-8333-444455556666",
  key: "BLOG",
  name: "Blog",
  capabilities: ADMIN_CAPABILITIES,
});

const respondWith = (projects: ApiResponseStub, currentProject: ApiResponseStub): void => {
  getRequest.mockImplementation((path) => {
    return Promise.resolve(path === "/api/projects" ? projects : currentProject);
  });
};

const renderSwitcher = (): ReturnType<typeof render> => {
  return render(
    <TestProviders queryClient={createTestQueryClient()}>
      <ProjectSwitcher />
    </TestProviders>,
  );
};

beforeEach(() => {
  navigation.pathname = "/projects/SHOP/settings";
  navigation.params = { projectKey: "SHOP" };
});

describe("ProjectSwitcher", () => {
  it("lists the projects, marks the current one and keeps an allowed section", async () => {
    respondWith(
      buildSuccessResponse([shopProject, docsProject, blogProject]),
      buildSuccessResponse(shopProject),
    );

    const { container } = renderSwitcher();
    const target = await screen.findByRole("button", {
      name: "Switch project, current: Shop SHOP",
    });

    expect(target).toHaveTextContent("SHOP");
    expect(await axe(container)).toHaveNoViolations();

    await userEvent.click(target);

    const currentItem = await screen.findByRole("menuitem", { name: "Shop (SHOP)", hidden: true });
    expect(screen.getByText("Your projects")).toBeInTheDocument();
    expect(currentItem).toHaveAttribute("href", "/projects/SHOP/settings");
    expect(currentItem.querySelector("svg")).toBeInTheDocument();
    expect(currentItem).toHaveAttribute("aria-current", "true");
    const docsItem = screen.getByRole("menuitem", { name: "Docs (DOCS)", hidden: true });
    expect(docsItem).toHaveAttribute("href", "/projects/DOCS");
    expect(docsItem).not.toHaveAttribute("aria-current");
    expect(docsItem.querySelector("svg")).not.toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Blog (BLOG)", hidden: true })).toHaveAttribute(
      "href",
      "/projects/BLOG/settings",
    );
    expect(screen.getByRole("menuitem", { name: "All projects", hidden: true })).toHaveAttribute(
      "href",
      "/projects",
    );
    expect(getRequest).toHaveBeenCalledWith("/api/projects", {
      params: { query: { includeArchived: false } },
    });
  });

  it("hides archived projects from the list but shows an archived current project", async () => {
    const archivedShop = buildProject({ isArchived: true, archivedAt: "2026-10-20T09:00:00Z" });
    respondWith(
      buildSuccessResponse([archivedShop, docsProject]),
      buildSuccessResponse(archivedShop),
    );

    renderSwitcher();

    expect(await screen.findByText("Archived")).toBeInTheDocument();

    await userEvent.click(
      screen.getByRole("button", { name: "Switch project, current: Shop SHOP Archived" }),
    );

    expect(
      await screen.findByRole("menuitem", { name: "Docs (DOCS)", hidden: true }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("menuitem", { name: "Shop (SHOP)", hidden: true }),
    ).not.toBeInTheDocument();
  });

  it("shows the placeholder and the empty item without projects", async () => {
    navigation.pathname = "/projects";
    navigation.params = {};
    respondWith(buildSuccessResponse([]), buildErrorResponse(404, "NOT_FOUND"));

    renderSwitcher();
    const target = screen.getByRole("button", { name: "Choose a project" });

    expect(target).toHaveTextContent("Choose a project");

    await userEvent.click(target);

    expect(
      await screen.findByRole("menuitem", { name: "No projects yet", hidden: true }),
    ).toBeDisabled();
  });

  it("shows a disabled error item when the projects fail to load", async () => {
    respondWith(buildErrorResponse(500, "INTERNAL_ERROR"), buildSuccessResponse(shopProject));

    renderSwitcher();
    await userEvent.click(
      await screen.findByRole("button", { name: "Switch project, current: Shop SHOP" }),
    );

    expect(
      await screen.findByRole("menuitem", { name: "Projects could not be loaded", hidden: true }),
    ).toBeDisabled();
  });
});
