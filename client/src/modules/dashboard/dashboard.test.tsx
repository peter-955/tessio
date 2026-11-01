import englishDashboard from "@/lib/i18n/locales/en/dashboard.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DashboardPage } from "./dashboard";
import { apiGet } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import {
  ACTIVE_SPRINT_ID,
  buildDashboard,
  buildSprintOption,
  CLOSED_SPRINT_ID,
} from "./test/utils/dashboard-fixture.util";
import { buildMyWork } from "./test/utils/my-work-fixture.util";
import { ADMIN_CAPABILITIES, buildProject } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { ABORTED_RUN_ID, buildRecentRun, RUN_ID } from "./test/utils/run-fixture.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface DashboardRequest {
  params: { path: { project_key: string }; query?: { sprintId: string } };
}

interface RunsRequest {
  params: { query: { limit: number } };
}

const DASHBOARD_PATH = "/api/projects/{project_key}/dashboard";
const MY_WORK_PATH = "/api/projects/{project_key}/my-work";
const RUNS_PATH = "/api/projects/{project_key}/runs";
const SPRINTS_PATH = "/api/projects/{project_key}/sprints";
const PAGE_PATH = "/projects/SHOP";

const { sprint, stats, testStatus, coverage, recentRuns } = englishDashboard;

const SPRINTS = [
  buildSprintOption(),
  buildSprintOption({
    id: CLOSED_SPRINT_ID,
    jiraSprintId: 11,
    name: "Sprint 11",
    state: "closed",
    startAt: "2026-09-30T00:00:00Z",
    endAt: "2026-10-14T00:00:00Z",
  }),
];

const RUNS = [
  buildRecentRun(),
  buildRecentRun({
    id: ABORTED_RUN_ID,
    storyJiraKey: "SHOP-2",
    storyTitle: "Refund a payment",
    executor: "manual",
    status: "aborted",
    abortReason: "no_results",
    environmentName: "QA",
    startedByName: "Bo Developer",
    counts: { total: 4, passed: 0, failed: 0, blocked: 0, skipped: 0, notReported: 4 },
  }),
];

interface Routes {
  dashboard?: ApiResult | (() => ApiResult);
  runs?: ApiResult;
  sprints?: ApiResult;
}

const respond = ({
  dashboard = createSuccessResult(buildDashboard()),
  runs = createSuccessResult(RUNS),
  sprints = createSuccessResult(SPRINTS),
}: Routes = {}): void => {
  respondWithRoutes(apiGet, {
    [DASHBOARD_PATH]: dashboard,
    [MY_WORK_PATH]: createSuccessResult(buildMyWork()),
    [RUNS_PATH]: runs,
    [SPRINTS_PATH]: sprints,
  });
};

const readRequests = <Request,>(path: string): Request[] => {
  return apiGet.mock.calls
    .filter(([calledPath]) => {
      return calledPath === path;
    })
    .map(([, options]) => {
      return options as Request;
    });
};

const renderPage = (
  initialSprintId: string | null = null,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <DashboardPage initialSprintId={initialSprintId} />,
    buildProject({ capabilities: ADMIN_CAPABILITIES }),
  );
};

const readStatValue = (label: string): string | null => {
  return screen.getByText(label, { selector: "dt" }).nextElementSibling?.textContent ?? null;
};

describe("DashboardPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respond();
  });

  it("shows the current sprint with its counts, status links and coverage", async () => {
    const { container } = renderPage();

    expect(await screen.findByText("Sprint 12")).toBeInTheDocument();
    expect(screen.getByText(sprint.states.active)).toBeInTheDocument();
    expect(screen.getByText("Oct 14, 2026 – Oct 28, 2026")).toBeInTheDocument();

    expect(readStatValue(stats.stories)).toBe("9");
    expect(screen.getByRole("link", { name: "9" })).toHaveAttribute(
      "href",
      `/projects/SHOP/stories?sprint=${ACTIVE_SPRINT_ID}`,
    );
    expect(readStatValue(stats.openGaps)).toBe("4");
    expect(readStatValue(stats.activeFailures)).toBe("6");
    expect(readStatValue(stats.coverage)).toBe("67%");

    const expectedRows: [string, string, string][] = [
      [testStatus.not_started, "1", "not_started"],
      [testStatus.ready_for_test, "2", "ready_for_test"],
      [testStatus.in_test, "3", "in_test"],
      [testStatus.passed, "2", "passed"],
      [testStatus.failed, "1", "failed"],
    ];
    const statusList = screen.getByRole("heading", { name: testStatus.title })
      .nextElementSibling as HTMLElement;
    const statusLinks = within(statusList).getAllByRole("link");
    expect(statusLinks).toHaveLength(5);
    expectedRows.forEach(([label, count, status], index) => {
      expect(statusLinks[index]).toHaveTextContent(`${label}${count}`);
      expect(statusLinks[index]).toHaveAttribute(
        "href",
        `/projects/SHOP/stories?sprint=${ACTIVE_SPRINT_ID}&status=${status}`,
      );
    });

    expect(screen.getByText("8 of 12 AC covered")).toBeInTheDocument();
    expect(
      screen.getByRole("img", {
        name: "5 passed, 2 failed, 0 blocked, 1 not run, 4 uncovered",
      }),
    ).toBeInTheDocument();
    const legendItems = screen
      .getAllByRole("listitem")
      .filter((item) => {
        return item.closest("ul")?.previousElementSibling?.getAttribute("role") === "img";
      })
      .map((item) => {
        return item.textContent;
      });
    expect(legendItems).toEqual([
      `${coverage.segments.passed}5`,
      `${coverage.segments.failed}2`,
      `${coverage.segments.notRun}1`,
      `${coverage.segments.uncovered}4`,
    ]);

    expect(readRequests<DashboardRequest>(DASHBOARD_PATH)[0].params.query).toBeUndefined();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("puts the chosen sprint in the URL and refetches the dashboard for it", async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText("Sprint 12");

    const option = await openSelectOption(
      user,
      new RegExp(`^${sprint.pickerLabel}`),
      `Sprint 11 · ${sprint.states.closed}`,
    );
    await user.click(option);

    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?sprint=${CLOSED_SPRINT_ID}`, {
      scroll: false,
    });
    await waitFor(() => {
      expect(readRequests<DashboardRequest>(DASHBOARD_PATH).at(-1)?.params.query).toEqual({
        sprintId: CLOSED_SPRINT_ID,
      });
    });
    expect(readRequests<DashboardRequest>(MY_WORK_PATH).at(-1)?.params.query).toEqual({
      sprintId: CLOSED_SPRINT_ID,
    });
  });

  it("shows the empty state when there is no active sprint", async () => {
    respond({ dashboard: createSuccessResult(buildDashboard({ sprint: null })) });
    const { container } = renderPage();

    expect(await screen.findByText(sprint.empty.title)).toBeInTheDocument();
    expect(screen.getByText(sprint.empty.description)).toBeInTheDocument();
    expect(
      await screen.findByRole("combobox", { name: new RegExp(`^${sprint.pickerLabel}`) }),
    ).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the not-found alert for an unknown sprint and resets to the current sprint", async () => {
    const user = userEvent.setup();
    const unknownSprintId = "9d9d9d9d-9d9d-4d9d-8d9d-9d9d9d9d9d9d";
    setNavigation(PAGE_PATH, `sprint=${unknownSprintId}`);
    respond({ dashboard: createErrorResult(404, "NOT_FOUND") });
    renderPage(unknownSprintId);

    expect(await screen.findByText(sprint.notFound.title)).toBeInTheDocument();
    expect(screen.getByText(sprint.notFound.description)).toBeInTheDocument();
    expect(readRequests<DashboardRequest>(DASHBOARD_PATH)[0].params.query).toEqual({
      sprintId: unknownSprintId,
    });

    await user.click(screen.getByRole("button", { name: sprint.notFound.reset }));

    expect(routerReplace).toHaveBeenLastCalledWith(PAGE_PATH, { scroll: false });
  });

  it("shows an error and refetches on retry", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond({
      dashboard: () => {
        return isFailing
          ? createErrorResult(500, "CONFLICT")
          : createSuccessResult(buildDashboard());
      },
    });
    renderPage();

    expect(await screen.findByText(sprint.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishDashboard.retry }));

    expect(await screen.findByText("8 of 12 AC covered")).toBeInTheDocument();
    expect(readRequests<DashboardRequest>(DASHBOARD_PATH)).toHaveLength(2);
  });

  it("lists the recent runs with links to the run detail", async () => {
    renderPage();

    const table = within(await screen.findByRole("table"));
    const runLink = table.getByRole("link", { name: "SHOP-1" });
    expect(runLink).toHaveAttribute("href", `/projects/SHOP/runs/${RUN_ID}`);
    expect(screen.getByRole("link", { name: recentRuns.viewAll })).toHaveAttribute(
      "href",
      "/projects/SHOP/runs",
    );
    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      recentRuns.columns.status,
      recentRuns.columns.story,
      recentRuns.columns.executor,
      recentRuns.columns.environment,
      recentRuns.columns.startedBy,
      recentRuns.columns.startedAt,
      recentRuns.columns.results,
    ]);

    const firstRow = within(runLink.closest("tr") as HTMLElement);
    expect(firstRow.getByText(recentRuns.status.passed)).toBeInTheDocument();
    expect(firstRow.getByText("Pay by card")).toBeInTheDocument();
    expect(firstRow.getByText(recentRuns.executor.claude)).toBeInTheDocument();
    expect(firstRow.getByText("Staging")).toBeInTheDocument();
    expect(firstRow.getByText("Ana Tester")).toBeInTheDocument();
    expect(firstRow.getByText("Oct 22, 08:00 AM UTC")).toBeInTheDocument();
    expect(firstRow.getByText("5 passed · 1 failed of 6")).toBeInTheDocument();

    const abortedLink = table.getByRole("link", { name: "SHOP-2" });
    expect(abortedLink).toHaveAttribute("href", `/projects/SHOP/runs/${ABORTED_RUN_ID}`);
    const abortedRow = within(abortedLink.closest("tr") as HTMLElement);
    expect(abortedRow.getByText(recentRuns.status.aborted)).toBeInTheDocument();
    expect(abortedRow.getByText(recentRuns.abortReason.no_results)).toBeInTheDocument();
    expect(abortedRow.getByText(recentRuns.executor.manual)).toBeInTheDocument();

    expect(readRequests<RunsRequest>(RUNS_PATH)[0].params.query).toEqual({ limit: 5 });
  });

  it("shows the recent runs empty state", async () => {
    respond({ runs: createSuccessResult([]) });
    const { container } = renderPage();

    expect(await screen.findByText(recentRuns.empty.title)).toBeInTheDocument();
    expect(screen.getByText(recentRuns.empty.description)).toBeInTheDocument();
    expect(screen.queryByRole("table")).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the recent runs error with a retry", async () => {
    respond({ runs: createErrorResult(500, "CONFLICT") });
    renderPage();

    expect(await screen.findByText(recentRuns.loadError)).toBeInTheDocument();
  });

  it("hides the sprint picker when there are no sprints", async () => {
    respond({ sprints: createSuccessResult([]) });
    renderPage();

    expect(await screen.findByText("Sprint 12")).toBeInTheDocument();
    expect(
      screen.queryByRole("combobox", { name: new RegExp(`^${sprint.pickerLabel}`) }),
    ).toBeNull();
  });
});
