import type { ProjectCapability } from "@/components/project-context/typing/types/project.type";
import englishPlans from "@/lib/i18n/locales/en/plans.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { PlansPage } from "./plans";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerPush } from "./test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import {
  ENVIRONMENT_ID,
  PLAN_ID,
  buildCounts,
  buildPlanDetail,
  buildPlanSummary,
} from "./test/utils/plan-fixture.util";
import {
  PM_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
  buildProject,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, string> };
}

interface PostRequest {
  body: Record<string, unknown>;
}

const PLANS_PATH = "/api/projects/{project_key}/plans";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";

const { list, form, toasts } = englishPlans;

const ENVIRONMENTS = [
  {
    id: ENVIRONMENT_ID,
    name: "Staging",
    baseUrl: "https://staging.example.test",
    healthCheckUrl: null,
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
  },
];

const respond = (plans: unknown = [buildPlanSummary()]): void => {
  respondWithRoutes(apiGet, {
    [PLANS_PATH]: createSuccessResult(plans),
    [ENVIRONMENTS_PATH]: createSuccessResult(ENVIRONMENTS),
  });
};

const renderPage = (
  capabilities: ProjectCapability[] = VIEWER_CAPABILITIES,
  isArchived = false,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<PlansPage />, buildProject({ capabilities, isArchived }));
};

const readListQueries = (): Record<string, string>[] => {
  return apiGet.mock.calls
    .filter(([path]) => {
      return path === PLANS_PATH;
    })
    .map(([, options]) => {
      return (options as ListRequest).params.query;
    });
};

describe("PlansPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    routerPush.mockReset();
  });

  it("lists the plans with their status, progress, target date and environment", async () => {
    respond();
    const { container } = renderPage();

    const table = await screen.findByRole("region", { name: list.label });
    const row = within(table).getByRole("row", { name: /Release 4\.2/ });
    expect(within(row).getByRole("link", { name: "Release 4.2" })).toHaveAttribute(
      "href",
      `/projects/SHOP/plans/${PLAN_ID}`,
    );
    expect(within(row).getByText("Open")).toBeInTheDocument();
    expect(within(row).getByText("2 of 4 cases passed")).toBeInTheDocument();
    expect(within(row).getByRole("progressbar", { name: "Passed: 2" })).toHaveAttribute(
      "aria-valuenow",
      "50",
    );
    expect(within(row).getByText("Staging")).toBeInTheDocument();
    expect(within(row).getByText("2 items")).toBeInTheDocument();
    expect(within(row).getByText(/Nov 20, 2026/)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows a plan with no case and no environment", async () => {
    respond([
      buildPlanSummary({
        environmentId: null,
        environmentName: null,
        targetDate: null,
        itemCount: 0,
        counts: buildCounts(),
      }),
    ]);
    renderPage();

    expect(await screen.findByText("No cases yet")).toBeInTheDocument();
    expect(screen.getByText(list.anyEnvironment)).toBeInTheDocument();
    expect(screen.getByText(list.noTargetDate)).toBeInTheDocument();
  });

  it("filters the list by status through the server", async () => {
    const user = userEvent.setup();
    respond();
    renderPage();

    await screen.findByRole("link", { name: "Release 4.2" });
    expect(readListQueries()).toEqual([{}]);

    respond([]);
    await user.click(screen.getByRole("radio", { name: list.filters.signed_off }));

    expect(await screen.findByText(list.empty.noMatch)).toBeInTheDocument();
    expect(readListQueries()).toContainEqual({ status: "signed_off" });

    respond();
    await user.click(screen.getByRole("button", { name: list.empty.showAll }));
    expect(await screen.findByRole("link", { name: "Release 4.2" })).toBeInTheDocument();
  });

  it("explains plans when the project has none, without a create button for a viewer", async () => {
    respond([]);
    renderPage();

    expect(await screen.findByText(list.empty.title)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: list.newPlan })).not.toBeInTheDocument();
  });

  it("offers New plan to a PM but not in an archived project", async () => {
    respond([]);
    const { unmount } = renderPage(PM_CAPABILITIES);

    await screen.findByText(list.empty.title);
    expect(screen.getAllByRole("button", { name: list.newPlan })).toHaveLength(2);
    unmount();

    respond([]);
    renderPage(PM_CAPABILITIES, true);
    await screen.findByText(list.empty.title);
    expect(screen.queryByRole("button", { name: list.newPlan })).not.toBeInTheDocument();
  });

  it("shows an error with a retry when the list fails", async () => {
    respondWithRoutes(apiGet, { [PLANS_PATH]: createErrorResult(500, "CONFLICT") });
    renderPage();

    expect(await screen.findByText(list.loadError)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: englishPlans.retry })).toBeInTheDocument();
  });

  it("creates a plan and opens it", async () => {
    const user = userEvent.setup();
    respond();
    apiPost.mockResolvedValue(createCreatedResult(buildPlanDetail()));
    renderPage(QC_CAPABILITIES);

    await user.click(await screen.findByRole("button", { name: list.newPlan }));
    const dialog = await screen.findByRole("dialog", { name: form.createTitle });

    await user.click(within(dialog).getByRole("button", { name: form.create }));
    expect(await within(dialog).findByText(form.nameRequired)).toBeInTheDocument();
    expect(apiPost).not.toHaveBeenCalled();

    await user.type(within(dialog).getByRole("textbox", { name: /Name/ }), "  Release 4.3 ");
    await user.type(
      within(dialog).getByRole("textbox", { name: form.description }),
      "The 4.3 release",
    );
    await user.click(await openSelectOption(user, /Environment/, "Staging"));
    await user.click(within(dialog).getByRole("button", { name: form.create }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledTimes(1);
    });
    const [path, options] = apiPost.mock.calls[0] ?? [];
    expect(path).toBe(PLANS_PATH);
    expect((options as PostRequest).body).toEqual({
      name: "Release 4.3",
      description: "The 4.3 release",
      environmentId: ENVIRONMENT_ID,
    });
    expect(await screen.findByText(toasts.created)).toBeInTheDocument();
    expect(routerPush).toHaveBeenCalledWith(`/projects/SHOP/plans/${PLAN_ID}`);
  });
});
