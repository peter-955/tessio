import englishRuns from "@/lib/i18n/locales/en/runs.json";
import englishSuites from "@/lib/i18n/locales/en/suites.json";
import { routerReplace, setNavigation } from "@/modules/auth/test/mocks/next-navigation.mock";
import { createSuccessResult, respondWithRoutes } from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { RunDetailPage } from "./run-detail";
import { RunsPage } from "./runs";
import { apiGet } from "./test/mocks/api-client.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { RUN_ID, createRunCase, createRunDetail, createRunSummary } from "./test/utils/run.fixture";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { RunDetailTab } from "./typing/enums/run-detail-tab.enum";
import { EMPTY_RUN_FILTERS } from "./utils/run-filters.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, string | number> };
}

const RUNS_PATH = "/api/projects/{project_key}/runs";
const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const SUITES_PATH = "/api/projects/{project_key}/suites";
const PAGE_PATH = "/projects/APP/runs";
const SUITE_ID = "5a000000-0000-4000-8000-000000000001";
const STORY_RUN_ID = "a6000000-0000-4000-8000-000000000020";

const { runs: suiteRuns, skipReason } = englishSuites;

const SUITE_RUN_FIELDS = {
  storyId: null,
  storyJiraKey: null,
  storyTitle: null,
  testSuiteId: SUITE_ID,
  testSuiteName: "Checkout regression",
};

const PAY_CASE = createRunCase({
  storyId: "c6000000-0000-4000-8000-000000000001",
  storyJiraKey: "APP-1",
  storyTitle: "Pay by card",
});

const REFUND_CASE = createRunCase({
  testCaseId: "d6000000-0000-4000-8000-000000000002",
  code: "TC-2",
  title: "Refund an order",
  position: 2,
  storyId: "c6000000-0000-4000-8000-000000000002",
  storyJiraKey: "APP-2",
  storyTitle: "Refunds",
  result: {
    id: "d6200000-0000-4000-8000-000000000002",
    status: "failed",
    durationMs: 3000,
    suspectedCause: null,
    causeReason: null,
    recordedAt: "2026-10-20T10:01:30Z",
    iteration: 0,
  },
});

const VOUCHER_CASE = createRunCase({
  testCaseId: "d6000000-0000-4000-8000-000000000003",
  code: "TC-3",
  title: "Pay with a voucher",
  position: 3,
  storyId: "c6000000-0000-4000-8000-000000000001",
  storyJiraKey: "APP-1",
  storyTitle: "Pay by card",
  result: null,
});

const SKIPPED_CASE = {
  testCaseId: "d6000000-0000-4000-8000-000000000004",
  code: "TC-4",
  title: "Pay in instalments",
  storyJiraKey: "APP-1",
  reason: "needs_review" as const,
};

const SUITE_RUN = createRunDetail({
  ...SUITE_RUN_FIELDS,
  cases: [PAY_CASE, REFUND_CASE, VOUCHER_CASE],
  skippedCases: [SKIPPED_CASE],
  report: {
    counts: { total: 3, passed: 1, failed: 1, blocked: 0, skipped: 0, notReported: 1 },
    failedCases: [
      {
        testCaseId: REFUND_CASE.testCaseId,
        code: "TC-2",
        title: "Refund an order",
        status: "failed",
        stepOrder: null,
        stepAction: null,
        actualResult: null,
        error: null,
        storyJiraKey: "APP-2",
      },
    ],
    criterionImpacts: [],
    missingScreenshots: [],
    summary: null,
    builtAt: "2026-10-20T10:03:00Z",
    unmappedTestCount: 0,
    stories: [
      {
        storyId: "c6000000-0000-4000-8000-000000000001",
        storyJiraKey: "APP-1",
        storyTitle: "Pay by card",
        counts: { total: 2, passed: 1, failed: 0, blocked: 0, skipped: 0, notReported: 1 },
      },
      {
        storyId: "c6000000-0000-4000-8000-000000000002",
        storyJiraKey: "APP-2",
        storyTitle: "Refunds",
        counts: { total: 1, passed: 0, failed: 1, blocked: 0, skipped: 0, notReported: 0 },
      },
    ],
    skippedCases: [SKIPPED_CASE],
  },
});

const readListQueries = (): Record<string, string | number>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === RUNS_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

describe("suite runs", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respondWithRoutes(apiGet, {
      [RUNS_PATH]: createSuccessResult([
        createRunSummary({ ...SUITE_RUN_FIELDS }),
        createRunSummary({ id: STORY_RUN_ID }),
      ]),
      [STORIES_PATH]: createSuccessResult([{ jiraKey: "APP-1", title: "Pay by card" }]),
      [SUITES_PATH]: createSuccessResult([
        {
          id: SUITE_ID,
          name: "Checkout regression",
          description: null,
          caseCount: 4,
          readyCaseCount: 3,
          archivedAt: null,
          createdAt: "2026-10-01T09:00:00Z",
          lastRun: null,
        },
      ]),
      [RUN_PATH]: createSuccessResult(SUITE_RUN),
    });
  });

  it("shows the suite of a suite run in the run list", async () => {
    const { container } = renderWithProject(<RunsPage initialFilters={EMPTY_RUN_FILTERS} />);

    const suiteLink = await screen.findByRole("link", { name: "Checkout regression" });
    expect(suiteLink).toHaveAttribute("href", `/projects/APP/suites/${SUITE_ID}`);
    const suiteRow = within(suiteLink.closest("tr") as HTMLElement);
    expect(suiteRow.getByText(suiteRuns.suiteBadge)).toBeInTheDocument();
    expect(within(screen.getByRole("table")).getByText("APP-1 · Pay by card")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("filters the run list by suite and drops the story filter", async () => {
    const user = userEvent.setup();
    renderWithProject(<RunsPage initialFilters={{ ...EMPTY_RUN_FILTERS, storyKey: "APP-1" }} />);
    await screen.findByRole("link", { name: "Checkout regression" });

    await user.click(await openSelectOption(user, /^Suite/, "Checkout regression"));

    await waitFor(() => {
      expect(readListQueries()).toContainEqual({ suiteId: SUITE_ID, limit: 50 });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?suite=${SUITE_ID}`, {
      scroll: false,
    });
  });

  it("names the suite and groups the results by story on the run page", async () => {
    const { container } = renderWithProject(
      <RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.RESULTS} />,
    );

    expect(
      await screen.findByRole("heading", { name: "Suite run · Checkout regression" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: suiteRuns.openSuite })).toHaveAttribute(
      "href",
      `/projects/APP/suites/${SUITE_ID}`,
    );
    const groups = within(screen.getByRole("group", { name: suiteRuns.storyGroupsLabel }));
    const payGroup = groups.getByRole("region", { name: "APP-1 · Pay by card" });
    const refundGroup = groups.getByRole("region", { name: "APP-2 · Refunds" });
    expect(within(payGroup).getByText("1 passed · 1 not reported")).toBeInTheDocument();
    expect(
      within(within(payGroup).getByRole("list")).getAllByRole("listitem", { hidden: false }),
    ).toHaveLength(2);
    expect(within(refundGroup).getByText("1 failed")).toBeInTheDocument();
    expect(within(refundGroup).getByText("Refund an order")).toBeInTheDocument();
    const skipped = within(screen.getByRole("list", { name: suiteRuns.skippedLabel }));
    expect(skipped.getByText("Pay in instalments")).toBeInTheDocument();
    expect(skipped.getByText(skipReason.needs_review)).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the results per story and the skipped cases in the report", async () => {
    renderWithProject(<RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.REPORT} />);

    const table = await screen.findByRole("region", { name: suiteRuns.reportStories });
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(within(rows[1]).getByRole("link", { name: "APP-1" })).toBeInTheDocument();
    expect(within(rows[1]).getByText("2 cases · 1 passed · 1 not reported")).toBeInTheDocument();
    expect(within(rows[2]).getByText("1 case · 1 failed")).toBeInTheDocument();
    expect(screen.getByText(englishRuns.report.failedCases)).toBeInTheDocument();
    expect(screen.getByText("APP-2", { selector: "span" })).toBeInTheDocument();
    expect(screen.getByText(suiteRuns.skippedTitle)).toBeInTheDocument();
  });

  it("keeps a story run's page as it was", async () => {
    respondWithRoutes(apiGet, { [RUN_PATH]: createSuccessResult(createRunDetail()) });
    renderWithProject(<RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.RESULTS} />);

    expect(await screen.findByRole("heading", { name: "Run on APP-1" })).toBeInTheDocument();
    expect(screen.getByRole("list", { name: englishRuns.case.listLabel })).toBeInTheDocument();
    expect(screen.queryByRole("group", { name: suiteRuns.storyGroupsLabel })).toBeNull();
  });
});
