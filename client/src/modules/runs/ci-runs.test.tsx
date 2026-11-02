import englishJunitImport from "@/lib/i18n/locales/en/junitImport.json";
import englishRuns from "@/lib/i18n/locales/en/runs.json";
import englishSuites from "@/lib/i18n/locales/en/suites.json";
import { setNavigation } from "@/modules/auth/test/mocks/next-navigation.mock";
import { createSuccessResult, respondWithRoutes } from "@/modules/auth/test/utils/api-result.util";
import { screen, within } from "@testing-library/react";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { RunDetailPage } from "./run-detail";
import { RunsPage } from "./runs";
import { apiGet } from "./test/mocks/api-client.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { RUN_ID, createRunCase, createRunDetail, createRunSummary } from "./test/utils/run.fixture";
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

const RUNS_PATH = "/api/projects/{project_key}/runs";
const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const SUITES_PATH = "/api/projects/{project_key}/suites";

const { ciRun, unmapped } = englishJunitImport;

const CI_RUN_FIELDS = {
  executor: "ci" as const,
  storyId: null,
  storyJiraKey: null,
  storyTitle: null,
  testSuiteId: null,
  testSuiteName: null,
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
});

const CI_RUN = createRunDetail({
  ...CI_RUN_FIELDS,
  status: "passed",
  summary: null,
  cases: [PAY_CASE, REFUND_CASE],
  report: {
    counts: { total: 2, passed: 2, failed: 0, blocked: 0, skipped: 0, notReported: 0 },
    failedCases: [],
    criterionImpacts: [],
    missingScreenshots: [],
    summary: null,
    builtAt: "2026-10-20T10:03:00Z",
    stories: [
      {
        storyId: "c6000000-0000-4000-8000-000000000001",
        storyJiraKey: "APP-1",
        storyTitle: "Pay by card",
        counts: { total: 1, passed: 1, failed: 0, blocked: 0, skipped: 0, notReported: 0 },
      },
      {
        storyId: "c6000000-0000-4000-8000-000000000002",
        storyJiraKey: "APP-2",
        storyTitle: "Refunds",
        counts: { total: 1, passed: 1, failed: 0, blocked: 0, skipped: 0, notReported: 0 },
      },
    ],
    skippedCases: [],
    unmappedTests: [
      {
        name: "loads the home page",
        classname: "home.spec.ts",
        status: "passed",
        reason: "no_case_code",
      },
    ],
    unmappedTestCount: 3,
  },
});

describe("CI runs", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    setNavigation("/projects/APP/runs");
    respondWithRoutes(apiGet, {
      [RUNS_PATH]: createSuccessResult([
        createRunSummary({ ...CI_RUN_FIELDS, status: "passed" }),
        createRunSummary({ id: "a6000000-0000-4000-8000-000000000020" }),
      ]),
      [STORIES_PATH]: createSuccessResult([]),
      [SUITES_PATH]: createSuccessResult([]),
      [RUN_PATH]: createSuccessResult(CI_RUN),
    });
  });

  it("shows the CI executor and the CI import target in the run list", async () => {
    const { container } = renderWithProject(<RunsPage initialFilters={EMPTY_RUN_FILTERS} />);

    const table = await screen.findByRole("table", { name: englishRuns.table.label });
    const ciRow = within(within(table).getAllByRole("row")[1]);
    expect(ciRow.getByText(englishRuns.executor.ci)).toBeInTheDocument();
    expect(ciRow.getByText(ciRun.target)).toBeInTheDocument();
    expect(ciRow.queryByText("·")).not.toBeInTheDocument();
    const storyRow = within(within(table).getAllByRole("row")[2]);
    expect(storyRow.getByText("APP-1 · Pay by card")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("names a CI import on the run page and groups its results by story", async () => {
    renderWithProject(<RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.RESULTS} />);

    expect(await screen.findByRole("heading", { name: ciRun.detailTitle })).toBeInTheDocument();
    expect(screen.getByText(ciRun.detailDescription)).toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: englishRuns.tabs.log })).not.toBeInTheDocument();
    const groups = within(screen.getByRole("group", { name: englishSuites.runs.storyGroupsLabel }));
    expect(groups.getByRole("region", { name: "APP-1 · Pay by card" })).toBeInTheDocument();
    expect(groups.getByRole("region", { name: "APP-2 · Refunds" })).toBeInTheDocument();
  });

  it("lists the unmapped tests and the stories in the report of a CI import", async () => {
    const { container } = renderWithProject(
      <RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.REPORT} />,
    );

    expect(await screen.findByRole("heading", { name: "3 unmapped tests" })).toBeInTheDocument();
    const table = within(screen.getByRole("region", { name: unmapped.tableLabel }));
    expect(table.getByText("loads the home page")).toBeInTheDocument();
    expect(table.getByText(unmapped.reasons.no_case_code)).toBeInTheDocument();
    expect(screen.getByText("2 more tests are not listed.")).toBeInTheDocument();
    expect(
      screen.getByRole("region", { name: englishSuites.runs.reportStories }),
    ).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
