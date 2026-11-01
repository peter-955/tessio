import { LAST_PROJECT_KEY_STORAGE_KEY } from "@/components/project-context/typing/constants/last-project-key.constant";
import englishDashboard from "@/lib/i18n/locales/en/dashboard.json";
import { TestProviders } from "@/test/test-providers";
import { createTestQueryClient } from "@/test/utils/create-test-query-client.util";
import { tabTo } from "@/test/utils/tab-to.util";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { buildProject } from "./test/utils/project-fixture.util";
import { WorkspaceHomePage } from "./workspace-home";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const PROJECTS_PATH = "/api/projects";

const PROJECTS = [
  buildProject({ id: "6f1c1d3e-8a59-4a39-9a43-1c6f0b3f2a11", key: "BILL", name: "Billing" }),
  buildProject(),
];

const respond = (result: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, { [PROJECTS_PATH]: result });
};

const renderPage = (): HTMLElement => {
  const { container } = render(
    <TestProviders queryClient={createTestQueryClient()}>
      <WorkspaceHomePage />
    </TestProviders>,
  );

  return container;
};

describe("WorkspaceHomePage", () => {
  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation("/");
    window.localStorage.clear();
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it("redirects to the last opened project", async () => {
    window.localStorage.setItem(LAST_PROJECT_KEY_STORAGE_KEY, "SHOP");
    respond(createSuccessResult(PROJECTS));
    renderPage();

    expect(document.querySelector('[aria-busy="true"]')).not.toBeNull();
    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/SHOP");
    });
  });

  it("redirects to the first project when the last one is gone", async () => {
    window.localStorage.setItem(LAST_PROJECT_KEY_STORAGE_KEY, "GONE");
    respond(createSuccessResult(PROJECTS));
    renderPage();

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/BILL");
    });
  });

  it("redirects to the projects list when there is no project", async () => {
    respond(createSuccessResult([]));
    renderPage();

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects");
    });
  });

  it("shows an error and retries", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing ? createErrorResult(500, "CONFLICT") : createSuccessResult(PROJECTS);
    });
    renderPage();

    expect(await screen.findByText(englishDashboard.home.loadError)).toBeInTheDocument();
    expect(routerReplace).not.toHaveBeenCalled();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishDashboard.retry }));

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/BILL");
    });
  });

  it("has no axe violations while loading and on error, and retries from the keyboard", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing ? createErrorResult(500, "CONFLICT") : createSuccessResult(PROJECTS);
    });
    const container = renderPage();

    expect(await axe(container)).toHaveNoViolations();
    expect(await screen.findByText(englishDashboard.home.loadError)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
    isFailing = false;
    await tabTo(user, screen.getByRole("button", { name: englishDashboard.retry }));
    await user.keyboard("{Enter}");

    await waitFor(() => {
      expect(routerReplace).toHaveBeenCalledWith("/projects/BILL");
    });
  });
});
