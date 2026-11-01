import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import englishTraceability from "@/lib/i18n/locales/en/traceability.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { TestCasesPage } from "./test-cases";
import { apiGet } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { buildCaseLatestResult } from "./test/utils/case-latest-result-fixture.util";
import { buildProject, QC_CAPABILITIES } from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import {
  buildStoryDetail,
  buildStorySummary,
  buildTestCaseSummary,
  SECOND_CRITERION_ID,
} from "./test/utils/test-case-fixture.util";
import { EMPTY_TEST_CASE_FILTERS } from "./utils/test-case-filters.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface ListRequest {
  params: { query: Record<string, string | boolean> };
}

const TEST_CASES_PATH = "/api/projects/{project_key}/test-cases";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const LATEST_RESULTS_PATH = "/api/projects/{project_key}/case-latest-results";
const PAGE_PATH = "/projects/SHOP/test-cases";

const { actions, empty, filters, status, table, loadError } = englishTestCases;

const TEST_CASES = [
  buildTestCaseSummary({ needsReview: true }),
  buildTestCaseSummary({
    id: "e1000000-0000-4000-8000-000000000002",
    code: "TC-2",
    storyKey: "SHOP-2",
    title: "Refund an order",
    status: "ready",
    priority: "low",
    stepCount: 5,
    criterionIds: [],
  }),
];

const LATEST_RESULTS = [
  buildCaseLatestResult(),
  buildCaseLatestResult({
    caseId: "e1000000-0000-4000-8000-000000000002",
    code: "TC-2",
    latestResult: null,
  }),
];

const respond = (
  testCases: ApiResult | (() => ApiResult),
  latestResults: ApiResult = createSuccessResult(LATEST_RESULTS),
): void => {
  respondWithRoutes(apiGet, {
    [TEST_CASES_PATH]: testCases,
    [LATEST_RESULTS_PATH]: latestResults,
    [STORIES_PATH]: createSuccessResult([
      buildStorySummary(),
      buildStorySummary({
        id: "c1000000-0000-4000-8000-000000000002",
        jiraKey: "SHOP-2",
        title: "Refunds",
      }),
    ]),
    [STORY_PATH]: createSuccessResult(buildStoryDetail()),
  });
};

const readListQueries = (): Record<string, string | boolean>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === TEST_CASES_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

const renderPage = (
  capabilities = QC_CAPABILITIES,
  initialFilters = EMPTY_TEST_CASE_FILTERS,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <TestCasesPage initialFilters={initialFilters} />,
    buildProject({ capabilities }),
  );
};

const chooseOption = async (user: UserEvent, label: string, option: string): Promise<void> => {
  await user.click(await openSelectOption(user, new RegExp(`^${label}`), option));
};

describe("TestCasesPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respond(createSuccessResult(TEST_CASES));
  });

  it("lists the cases with their story, status, priority and counts", async () => {
    const { container } = renderPage();

    const codeLink = await screen.findByRole("link", { name: "TC-1" });
    expect(codeLink).toHaveAttribute("href", "/projects/SHOP/test-cases/TC-1");
    const row = within(codeLink.closest("tr") as HTMLElement);
    expect(row.getByText("Pay with a valid card")).toBeInTheDocument();
    expect(row.getByRole("link", { name: "SHOP-1" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-1",
    );
    expect(row.getByText(status.draft)).toBeInTheDocument();
    expect(row.getByText(table.needsReview)).toBeInTheDocument();
    expect(row.getByText(englishTestCases.priority.high)).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").map((header) => header.textContent)).toEqual([
      table.code,
      table.title,
      table.story,
      table.priority,
      table.status,
      englishTraceability.caseColumns.latestResult,
      table.steps,
      table.criteria,
      table.lastSaved,
    ]);
    expect(screen.getByRole("button", { name: actions.import })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: actions.new })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/new",
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the latest result of each case", async () => {
    renderPage();

    const firstRow = within(
      (await screen.findByRole("link", { name: "TC-1" })).closest("tr") as HTMLElement,
    );
    expect(await firstRow.findByText(englishTraceability.resultStatus.failed)).toBeInTheDocument();
    const secondRow = within(
      screen.getByRole("link", { name: "TC-2" }).closest("tr") as HTMLElement,
    );
    expect(secondRow.getByText(englishTraceability.resultStatus.not_run)).toBeInTheDocument();
    expect(
      apiGet.mock.calls
        .filter(([path]) => path === LATEST_RESULTS_PATH)
        .map(([, options]) => (options as ListRequest).params.query),
    ).toEqual([{}]);
  });

  it("keeps the list when the latest results cannot be loaded", async () => {
    respond(createSuccessResult(TEST_CASES), createErrorResult(500, "CONFLICT"));
    renderPage();

    const firstRow = within(
      (await screen.findByRole("link", { name: "TC-1" })).closest("tr") as HTMLElement,
    );
    expect(await firstRow.findByText(englishTraceability.storyColumns.unknown)).toBeInTheDocument();
    expect(firstRow.queryByText(englishTraceability.resultStatus.failed)).toBeNull();
  });

  it("puts the filters in the URL and the list query", async () => {
    const user = userEvent.setup();
    renderPage();

    await screen.findByRole("link", { name: "TC-1" });
    await chooseOption(user, filters.story, "SHOP-1 · Pay by card");

    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?story=SHOP-1`, { scroll: false });
    await chooseOption(user, filters.criterion, "AC2 · Declined card shows an error");
    expect(routerReplace).toHaveBeenLastCalledWith(
      `${PAGE_PATH}?story=SHOP-1&criterion=${SECOND_CRITERION_ID}`,
      { scroll: false },
    );
    await chooseOption(user, filters.status, status.ready);
    await user.click(screen.getByRole("checkbox", { name: filters.needsReview }));
    await user.type(screen.getByRole("textbox", { name: filters.search }), "refund");

    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({
        storyKey: "SHOP-1",
        criterionId: SECOND_CRITERION_ID,
        status: "ready",
        needsReview: true,
        query: "refund",
      });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(
      `${PAGE_PATH}?story=SHOP-1&status=ready&criterion=${SECOND_CRITERION_ID}&needsReview=true&query=refund`,
      { scroll: false },
    );
  });

  it("clears the criterion when the story changes", async () => {
    const user = userEvent.setup();
    renderPage(QC_CAPABILITIES, {
      ...EMPTY_TEST_CASE_FILTERS,
      storyKey: "SHOP-1",
      criterionId: SECOND_CRITERION_ID,
    });

    await screen.findByRole("link", { name: "TC-1" });
    await chooseOption(user, filters.story, "SHOP-2 · Refunds");

    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?story=SHOP-2`, { scroll: false });
  });

  it("disables the criterion filter until a story is chosen", async () => {
    renderPage();

    await screen.findByRole("link", { name: "TC-1" });

    expect(
      screen.getByRole("combobox", { name: new RegExp(`^${filters.criterion}`) }),
    ).toBeDisabled();
  });

  it("shows the empty state with the editor actions", async () => {
    respond(createSuccessResult([]));
    renderPage();

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: actions.import })).toHaveLength(2);
    expect(screen.getAllByRole("link", { name: actions.new })).toHaveLength(2);
  });

  it("shows the no-match state and clears the filters", async () => {
    const user = userEvent.setup();
    respond(createSuccessResult([]));
    renderPage(QC_CAPABILITIES, { ...EMPTY_TEST_CASE_FILTERS, status: "ready" });

    expect(await screen.findByText(empty.noMatch)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: actions.clearFilters }));

    expect(routerReplace).toHaveBeenLastCalledWith(PAGE_PATH, { scroll: false });
  });

  it("shows an error with a retry", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond(() => {
      return isFailing
        ? createErrorResult(500, "INVALID_REQUEST")
        : createSuccessResult(TEST_CASES);
    });
    renderPage();

    expect(await screen.findByText(loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishTestCases.retry }));

    expect(await screen.findByRole("link", { name: "TC-1" })).toBeInTheDocument();
  });

  it("hides New and Import from a viewer", async () => {
    respond(createSuccessResult([]));
    renderPage(buildProject().capabilities);

    expect(await screen.findByText(empty.title)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.import })).toBeNull();
    expect(screen.queryByRole("link", { name: actions.new })).toBeNull();
  });

  it("hides New and Import on an archived project", async () => {
    renderWithProject(
      <TestCasesPage initialFilters={EMPTY_TEST_CASE_FILTERS} />,
      buildProject({ capabilities: QC_CAPABILITIES, isArchived: true }),
    );

    await screen.findByRole("link", { name: "TC-1" });
    expect(screen.queryByRole("button", { name: actions.import })).toBeNull();
    expect(screen.queryByRole("link", { name: actions.new })).toBeNull();
  });
});
