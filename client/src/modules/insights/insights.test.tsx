import englishInsights from "@/lib/i18n/locales/en/insights.json";
import type { Sprint } from "@/modules/sprints/typing/types/sprint.type";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterAll, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { InsightsPage } from "./insights";
import { apiGet } from "./test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import {
  buildEmptyTrends,
  buildFailingCase,
  buildFlakyCase,
  buildLabelCoverage,
  buildSprintCoverage,
  buildTokenUsage,
  buildTrends,
  SPRINT_ID,
} from "./test/utils/insights-fixture.util";
import { buildProject } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

interface RangeRequest {
  params: { path: { project_key: string }; query: Record<string, string | number> };
}

const TRENDS_PATH = "/api/projects/{project_key}/insights/trends";
const LABELS_PATH = "/api/projects/{project_key}/insights/coverage-by-label";
const TOP_FAILING_PATH = "/api/projects/{project_key}/insights/top-failing";
const FLAKY_PATH = "/api/projects/{project_key}/insights/flaky";
const TOKENS_PATH = "/api/projects/{project_key}/insights/tokens";
const SPRINT_COVERAGE_PATH = "/api/projects/{project_key}/insights/sprint-coverage";
const SPRINTS_PATH = "/api/projects/{project_key}/sprints";
const TODAY = new Date("2026-11-02T12:00:00Z");

const { summary, labels, topFailing, flaky, tokens, sprintCoverage, filters } = englishInsights;

const SPRINT: Sprint = {
  id: SPRINT_ID,
  jiraSprintId: 12,
  name: "Sprint 12",
  state: "closed",
  startAt: "2026-10-15T00:00:00Z",
  endAt: "2026-10-29T00:00:00Z",
  completeAt: null,
  storyCount: 3,
  syncedAt: "2026-10-30T09:00:00Z",
};

interface Routes {
  trends?: ApiResult | (() => ApiResult);
  labelCoverage?: ApiResult;
  topFailing?: ApiResult;
  flakyCases?: ApiResult;
  tokenUsage?: ApiResult;
  sprintCoverageItems?: ApiResult;
}

const respond = ({
  trends = createSuccessResult(buildTrends()),
  labelCoverage = createSuccessResult(buildLabelCoverage()),
  topFailing: topFailingResult = createSuccessResult([buildFailingCase()]),
  flakyCases = createSuccessResult([buildFlakyCase()]),
  tokenUsage = createSuccessResult(buildTokenUsage()),
  sprintCoverageItems = createSuccessResult([buildSprintCoverage()]),
}: Routes = {}): void => {
  respondWithRoutes(apiGet, {
    [TRENDS_PATH]: trends,
    [LABELS_PATH]: labelCoverage,
    [TOP_FAILING_PATH]: topFailingResult,
    [FLAKY_PATH]: flakyCases,
    [TOKENS_PATH]: tokenUsage,
    [SPRINT_COVERAGE_PATH]: sprintCoverageItems,
    [SPRINTS_PATH]: createSuccessResult([SPRINT]),
  });
};

const readQueries = (path: string): Record<string, string | number>[] => {
  return apiGet.mock.calls
    .filter(([calledPath]) => {
      return calledPath === path;
    })
    .map(([, options]) => {
      return (options as RangeRequest).params.query;
    });
};

const readStatValue = (label: string): string | null => {
  return screen.getByText(label, { selector: "dt" }).nextElementSibling?.textContent ?? null;
};

const readChartRow = (chartName: string, rowName: string): string[] => {
  const figure = screen.getByRole("figure", { name: chartName });
  const table = within(figure).getByRole("table", { name: chartName });
  const row = within(table).getByRole("rowheader", { name: rowName }).closest("tr");

  return within(row as HTMLElement)
    .getAllByRole("cell")
    .map((cell) => {
      return cell.textContent ?? "";
    });
};

const renderPage = (): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<InsightsPage />, buildProject());
};

describe("InsightsPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(TODAY);
  });

  afterAll(() => {
    vi.useRealTimers();
  });

  beforeEach(() => {
    apiGet.mockReset();
    respond();
  });

  it("shows the trends, case lists, coverage and tokens of the last 30 days", async () => {
    const { container } = renderPage();

    expect(await screen.findByText(summary.passRate, { selector: "dt" })).toBeInTheDocument();
    expect(readStatValue(summary.passRate)).toBe("81.3%");
    expect(readStatValue(summary.runs)).toBe("4");
    expect(readStatValue(summary.results)).toBe("6 / 1 / 1");
    expect(readStatValue(summary.failuresFixed)).toBe("4");
    expect(readStatValue(summary.meanTimeToFix)).toBe("2 hr");
    expect(readStatValue(summary.medianOpenGapAge)).toBe("2 days");

    expect(readChartRow(englishInsights.passRate.title, "Nov 1, 2026")).toEqual(["75%"]);
    expect(readChartRow(englishInsights.executors.title, "Nov 1, 2026")).toEqual(["1", "1"]);
    expect(readChartRow(englishInsights.failures.title, "Oct 31, 2026")).toEqual(["1", "2"]);
    expect(readChartRow(englishInsights.gaps.title, "Nov 1, 2026")).toEqual(["2 days", "1 day"]);

    const failingTable = await screen.findByRole("region", { name: topFailing.title });
    expect(within(failingTable).getByRole("link", { name: "TC-7" })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/TC-7",
    );
    expect(within(failingTable).getByText("2 / 1 of 5")).toBeInTheDocument();
    expect(within(failingTable).getByText("60%")).toBeInTheDocument();

    const flakyTable = await screen.findByRole("region", { name: flaky.title });
    expect(within(flakyTable).getByRole("link", { name: "TC-9" })).toBeInTheDocument();
    expect(within(flakyTable).getByText("4 flips in 10 results")).toBeInTheDocument();

    expect(await screen.findByRole("figure", { name: labels.chart })).toBeInTheDocument();
    expect(readChartRow(labels.chart, "checkout")).toEqual(["75%", "50%"]);
    const labelTable = screen.getByRole("region", { name: labels.table });
    expect(within(labelTable).getByText(labels.unlabelled)).toBeInTheDocument();
    expect(within(labelTable).getByText("3 (75%)")).toBeInTheDocument();

    expect(await screen.findByRole("figure", { name: sprintCoverage.title })).toBeInTheDocument();
    expect(readChartRow(sprintCoverage.title, "Sprint 12")).toEqual(["5", "1", "1", "1", "2"]);

    expect(await screen.findByText(tokens.total, { selector: "dt" })).toBeInTheDocument();
    expect(readStatValue(tokens.total)).toBe("8K");
    const tokenTable = screen.getByRole("region", { name: tokens.table });
    expect(within(tokenTable).getByRole("link", { name: "Checkout regression" })).toHaveAttribute(
      "href",
      "/projects/SHOP/runs/60718293-a4b5-4c63-d7e8-f9a0b1c2d3e4",
    );
    expect(within(tokenTable).getByText(tokens.cut)).toBeInTheDocument();

    expect(readQueries(TRENDS_PATH)[0]).toEqual({
      from: "2026-10-04",
      to: "2026-11-02",
      groupBy: "day",
    });
    expect(readQueries(TOP_FAILING_PATH)[0]).toEqual({
      from: "2026-10-04",
      to: "2026-11-02",
      limit: 10,
    });
    expect(readQueries(TOKENS_PATH)[0]).toEqual({ from: "2026-10-04", to: "2026-11-02" });
    expect(readQueries(SPRINT_COVERAGE_PATH)[0]).toEqual({
      from: "2026-10-04",
      to: "2026-11-02",
    });
    expect(readQueries(FLAKY_PATH)[0]).toEqual({ limit: 10 });
    expect(await axe(container)).toHaveNoViolations();
  });

  it("uses the chosen sprint's dates and groups the trends by sprint", async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByText(summary.passRate, { selector: "dt" });

    const option = await openSelectOption(
      user,
      new RegExp(`^${filters.sprint}`),
      `Sprint 12 · ${filters.sprintStates.closed}`,
    );
    await user.click(option);

    await waitFor(() => {
      expect(readQueries(TRENDS_PATH).at(-1)).toEqual({
        from: "2026-10-15",
        to: "2026-10-29",
        groupBy: "day",
      });
    });
    expect(readQueries(TOKENS_PATH).at(-1)).toEqual({ from: "2026-10-15", to: "2026-10-29" });

    await user.click(screen.getByRole("radio", { name: filters.groupBy.sprint }));

    await waitFor(() => {
      expect(readQueries(TRENDS_PATH).at(-1)).toEqual({
        from: "2026-10-15",
        to: "2026-10-29",
        groupBy: "sprint",
      });
    });
  });

  it("shows empty states when nothing happened", async () => {
    respond({
      trends: createSuccessResult(buildEmptyTrends()),
      labelCoverage: createSuccessResult({
        labels: [],
        unlabelled: {
          caseCount: 0,
          readyCount: 0,
          passedCount: 0,
          readyShare: null,
          passedShare: null,
        },
        total: { caseCount: 0, readyCount: 0, passedCount: 0, readyShare: null, passedShare: null },
      }),
      topFailing: createSuccessResult([]),
      flakyCases: createSuccessResult([]),
      tokenUsage: createSuccessResult(
        buildTokenUsage({
          runs: [],
          totalTokens: 0,
          meanTokensPerRun: null,
          meanTokensPerCase: null,
        }),
      ),
      sprintCoverageItems: createSuccessResult([]),
    });
    const { container } = renderPage();

    expect(await screen.findByText(summary.emptyTitle)).toBeInTheDocument();
    expect(await screen.findByText(topFailing.emptyTitle)).toBeInTheDocument();
    expect(await screen.findByText(flaky.emptyTitle)).toBeInTheDocument();
    expect(await screen.findByText(labels.emptyTitle)).toBeInTheDocument();
    expect(await screen.findByText(sprintCoverage.emptyTitle)).toBeInTheDocument();
    expect(await screen.findByText(tokens.emptyTitle)).toBeInTheDocument();
    expect(screen.queryByRole("figure", { name: englishInsights.passRate.title })).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows an error for the trends and refetches on retry", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond({
      trends: () => {
        return isFailing
          ? createErrorResult(500, "INVALID_REQUEST")
          : createSuccessResult(buildTrends());
      },
    });
    renderPage();

    expect(await screen.findByText(`Could not load ${summary.title}.`)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishInsights.retry }));

    expect(await screen.findByText(summary.passRate, { selector: "dt" })).toBeInTheDocument();
  });
});
