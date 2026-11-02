import type { ProjectCapability } from "@/components/project-context/typing/types/project.type";
import englishFlakyCases from "@/lib/i18n/locales/en/flakyCases.json";
import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { TestCaseDetailPage } from "./test-case-detail";
import { TestCasesPage } from "./test-cases";
import { apiDelete, apiGet, apiPut } from "./test/mocks/api-client.mock";
import { routerReplace, setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import { buildCaseLatestResult } from "./test/utils/case-latest-result-fixture.util";
import { interpolate } from "./test/utils/interpolate.util";
import {
  buildProject,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import {
  buildMember,
  buildStoryDetail,
  buildStorySummary,
  buildTestCaseDetail,
  buildTestCaseSummary,
  QC_USER_ID,
} from "./test/utils/test-case-fixture.util";
import { TestCaseDetailTab } from "./typing/enums/test-case-detail-tab.enum";
import type { QuarantineEvent } from "./typing/types/quarantine.type";
import type { TestCaseDetail } from "./typing/types/test-case.type";
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
const LATEST_RESULTS_PATH = "/api/projects/{project_key}/case-latest-results";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const STORY_PATH = "/api/projects/{project_key}/stories/{jira_key}";
const LABELS_PATH = "/api/projects/{project_key}/labels";
const CASE_PATH = "/api/projects/{project_key}/test-cases/{case_code}";
const VERSIONS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/versions";
const QUARANTINE_PATH = "/api/projects/{project_key}/test-cases/{case_code}/quarantine";
const QUARANTINE_EVENTS_PATH =
  "/api/projects/{project_key}/test-cases/{case_code}/quarantine-events";
const REVIEW_COMMENTS_PATH = "/api/projects/{project_key}/test-cases/{case_code}/review-comments";
const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";
const EFFECTIVE_TEST_DATA_PATH = "/api/projects/{project_key}/test-data/effective";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const MEMBERS_PATH = "/api/projects/{project_key}/members";
const PAGE_PATH = "/projects/SHOP/test-cases";
const CASE_PARAMS = { params: { path: { project_key: "SHOP", case_code: "TC-1" } } };

const QUARANTINE_CAPABILITIES: ProjectCapability[] = [...QC_CAPABILITIES, "test_case.quarantine"];

const { badges, filters, alerts, actions, modal, toasts, history } = englishFlakyCases;

const FLAKY_CASE = buildTestCaseSummary({ isFlaky: true, flakyScore: 4 });

const DISAGREEING_CASE = buildTestCaseSummary({
  id: "e1000000-0000-4000-8000-000000000002",
  code: "TC-2",
  title: "Refund an order",
  isDisagreeing: true,
});

const QUARANTINED_CASE = buildTestCaseSummary({
  id: "e1000000-0000-4000-8000-000000000003",
  code: "TC-3",
  title: "Cancel an order",
  isQuarantined: true,
  quarantinedAt: "2026-10-23T09:00:00Z",
});

const HEALTHY_CASE = buildTestCaseSummary({
  id: "e1000000-0000-4000-8000-000000000004",
  code: "TC-4",
  title: "Browse the catalogue",
});

const QUARANTINED_DETAIL = buildTestCaseDetail({
  isQuarantined: true,
  quarantinedAt: "2026-10-23T09:00:00Z",
  quarantinedBy: QC_USER_ID,
  quarantineReason: "Payment sandbox times out",
});

const QUARANTINE_EVENTS: QuarantineEvent[] = [
  {
    id: "a7000000-0000-4000-8000-000000000003",
    kind: "auto_released",
    actorId: null,
    actorName: null,
    reason: null,
    createdAt: "2026-10-25T09:00:00Z",
  },
  {
    id: "a7000000-0000-4000-8000-000000000002",
    kind: "quarantined",
    actorId: QC_USER_ID,
    actorName: "Quinn Tester",
    reason: "Payment sandbox times out",
    createdAt: "2026-10-23T09:00:00Z",
  },
  {
    id: "a7000000-0000-4000-8000-000000000001",
    kind: "released",
    actorId: null,
    actorName: null,
    reason: null,
    createdAt: "2026-10-22T09:00:00Z",
  },
];

const respondWithList = (testCases: ApiResult): void => {
  respondWithRoutes(apiGet, {
    [TEST_CASES_PATH]: testCases,
    [LATEST_RESULTS_PATH]: createSuccessResult([buildCaseLatestResult()]),
    [STORIES_PATH]: createSuccessResult([buildStorySummary()]),
    [STORY_PATH]: createSuccessResult(buildStoryDetail()),
    [LABELS_PATH]: createSuccessResult([]),
  });
};

const respondWithCase = (detail: TestCaseDetail, events: QuarantineEvent[] = []): void => {
  respondWithRoutes(apiGet, {
    [CASE_PATH]: createSuccessResult(detail),
    [VERSIONS_PATH]: createSuccessResult([detail.currentVersion]),
    [QUARANTINE_EVENTS_PATH]: createSuccessResult(events),
    [REVIEW_COMMENTS_PATH]: createSuccessResult([]),
    [STORY_PATH]: createSuccessResult(buildStoryDetail()),
    [LABELS_PATH]: createSuccessResult([]),
    [TEST_DATA_PATH]: createSuccessResult([]),
    [EFFECTIVE_TEST_DATA_PATH]: createSuccessResult([]),
    [ENVIRONMENTS_PATH]: createSuccessResult([]),
    [MEMBERS_PATH]: createSuccessResult([buildMember()]),
  });
};

const readListQueries = (): Record<string, string | boolean>[] => {
  return apiGet.mock.calls
    .filter(([path]) => path === TEST_CASES_PATH)
    .map(([, options]) => (options as ListRequest).params.query);
};

const renderList = (
  initialFilters = EMPTY_TEST_CASE_FILTERS,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <TestCasesPage initialFilters={initialFilters} />,
    buildProject({ capabilities: QC_CAPABILITIES }),
  );
};

const renderDetail = (
  capabilities: ProjectCapability[] = QUARANTINE_CAPABILITIES,
  options: { initialTab?: TestCaseDetailTab; isArchived?: boolean } = {},
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <TestCaseDetailPage
      caseCode="TC-1"
      initialTab={options.initialTab ?? TestCaseDetailTab.DETAILS}
    />,
    buildProject({ capabilities, isArchived: options.isArchived ?? false }),
  );
};

const findRow = async (code: string): Promise<ReturnType<typeof within>> => {
  const codeLink = await screen.findByRole("link", { name: code });

  return within(codeLink.closest("tr") as HTMLElement);
};

describe("flaky cases on the case list", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    routerReplace.mockReset();
    setNavigation(PAGE_PATH);
    respondWithList(
      createSuccessResult([FLAKY_CASE, DISAGREEING_CASE, QUARANTINED_CASE, HEALTHY_CASE]),
    );
  });

  it("shows a flaky, disagreeing or quarantined badge on each row that has the flag", async () => {
    const { container } = renderList();

    const flakyRow = await findRow("TC-1");
    expect(flakyRow.getByText(badges.flaky)).toBeInTheDocument();
    expect(flakyRow.queryByText(badges.quarantined)).toBeNull();
    expect((await findRow("TC-2")).getByText(badges.disagreeing)).toBeInTheDocument();
    expect((await findRow("TC-3")).getByText(badges.quarantined)).toBeInTheDocument();
    const healthyRow = await findRow("TC-4");
    expect(healthyRow.queryByText(badges.flaky)).toBeNull();
    expect(healthyRow.queryByText(badges.disagreeing)).toBeNull();
    expect(healthyRow.queryByText(badges.quarantined)).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("puts the flaky, disagreeing and quarantined filters in the URL and the list query", async () => {
    const user = userEvent.setup();
    renderList();

    await screen.findByRole("link", { name: "TC-1" });
    await user.click(screen.getByRole("checkbox", { name: filters.flaky }));
    expect(routerReplace).toHaveBeenLastCalledWith(`${PAGE_PATH}?flaky=true`, { scroll: false });
    await user.click(screen.getByRole("checkbox", { name: filters.disagreeing }));
    await user.click(screen.getByRole("checkbox", { name: filters.quarantined }));

    await waitFor(() => {
      expect(readListQueries().at(-1)).toEqual({
        flaky: true,
        disagreeing: true,
        quarantined: true,
      });
    });
    expect(routerReplace).toHaveBeenLastCalledWith(
      `${PAGE_PATH}?flaky=true&disagreeing=true&quarantined=true`,
      { scroll: false },
    );

    await user.click(screen.getByRole("checkbox", { name: filters.flaky }));
    expect(routerReplace).toHaveBeenLastCalledWith(
      `${PAGE_PATH}?disagreeing=true&quarantined=true`,
      { scroll: false },
    );
  });

  it("reads the filters from the page props and clears them from the no-match state", async () => {
    const user = userEvent.setup();
    respondWithList(createSuccessResult([]));
    renderList({ ...EMPTY_TEST_CASE_FILTERS, isQuarantined: true });

    expect(await screen.findByText(englishTestCases.empty.noMatch)).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: filters.quarantined })).toBeChecked();
    expect(readListQueries().at(-1)).toEqual({ quarantined: true });
    await user.click(screen.getByRole("button", { name: englishTestCases.actions.clearFilters }));

    expect(routerReplace).toHaveBeenLastCalledWith(PAGE_PATH, { scroll: false });
  });
});

describe("flaky cases on the case detail", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    apiDelete.mockReset();
    routerReplace.mockReset();
    setNavigation("/projects/SHOP/test-cases/TC-1");
    respondWithCase(buildTestCaseDetail());
  });

  it("explains a flaky and disagreeing case with badges and alerts", async () => {
    respondWithCase(
      buildTestCaseDetail({
        isFlaky: true,
        flakyScore: 4,
        flakySince: "2026-10-22T09:00:00Z",
        isDisagreeing: true,
        disagreedAt: "2026-10-23T09:00:00Z",
      }),
    );
    const { container } = renderDetail();

    expect(await screen.findByText(alerts.flakyTitle)).toBeInTheDocument();
    expect(screen.getByText(/^4 pass\/fail flips in the last 10 results/)).toBeInTheDocument();
    expect(screen.getByText(alerts.disagreeingTitle)).toBeInTheDocument();
    expect(screen.getByText(badges.flaky)).toBeInTheDocument();
    expect(screen.getByText(badges.disagreeing)).toBeInTheDocument();
    expect(screen.queryByText(alerts.quarantinedTitle)).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows no flaky alert for a healthy case", async () => {
    renderDetail();

    expect(await screen.findByRole("button", { name: actions.quarantine })).toBeInTheDocument();
    expect(screen.queryByText(alerts.flakyTitle)).toBeNull();
    expect(screen.queryByText(alerts.disagreeingTitle)).toBeNull();
    expect(screen.queryByText(badges.quarantined)).toBeNull();
  });

  it("quarantines a case with a trimmed reason", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, { [QUARANTINE_PATH]: createSuccessResult(QUARANTINED_DETAIL) });
    renderDetail();

    await user.click(await screen.findByRole("button", { name: actions.quarantine }));
    const dialog = await screen.findByRole("dialog", {
      name: interpolate(modal.title, { code: "TC-1" }),
    });
    await user.type(
      within(dialog).getByRole("textbox", { name: new RegExp(`^${modal.reason}`) }),
      "  Payment sandbox times out  ",
    );
    expect(apiPut).not.toHaveBeenCalled();
    await user.click(within(dialog).getByRole("button", { name: actions.quarantine }));

    expect(apiPut).toHaveBeenCalledWith(QUARANTINE_PATH, {
      ...CASE_PARAMS,
      body: { reason: "Payment sandbox times out" },
    });
    expect(
      await screen.findByText(interpolate(toasts.quarantined, { code: "TC-1" })),
    ).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: actions.release })).toBeInTheDocument();
    expect(screen.getByText(alerts.quarantinedTitle)).toBeInTheDocument();
    expect(
      screen.getByText(
        interpolate(alerts.quarantinedReason, { reason: "Payment sandbox times out" }),
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(/, by Quinn Tester\.$/)).toBeInTheDocument();
  });

  it("quarantines without a reason when the reason is blank", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPut, { [QUARANTINE_PATH]: createSuccessResult(QUARANTINED_DETAIL) });
    renderDetail();

    await user.click(await screen.findByRole("button", { name: actions.quarantine }));
    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByRole("button", { name: actions.quarantine }));

    expect(apiPut).toHaveBeenCalledWith(QUARANTINE_PATH, { ...CASE_PARAMS, body: {} });
  });

  it("releases a quarantined case", async () => {
    const user = userEvent.setup();
    respondWithCase(QUARANTINED_DETAIL);
    respondWithRoutes(apiDelete, { [QUARANTINE_PATH]: createSuccessResult(buildTestCaseDetail()) });
    renderDetail();

    expect(await screen.findByText(alerts.quarantineNote)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: actions.release }));

    expect(apiDelete).toHaveBeenCalledWith(QUARANTINE_PATH, CASE_PARAMS);
    expect(
      await screen.findByText(interpolate(toasts.released, { code: "TC-1" })),
    ).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: actions.quarantine })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText(alerts.quarantinedTitle)).toBeNull();
    });
  });

  it("hides the quarantine actions without test_case.quarantine and on an archived project", async () => {
    respondWithCase(QUARANTINED_DETAIL);
    const viewerPage = renderDetail(VIEWER_CAPABILITIES);

    expect(await screen.findByText(alerts.quarantinedTitle)).toBeInTheDocument();
    expect(screen.getByText(badges.quarantined)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.release })).toBeNull();
    viewerPage.unmount();

    const editorPage = renderDetail(QC_CAPABILITIES);
    expect(await screen.findByText(alerts.quarantinedTitle)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.release })).toBeNull();
    editorPage.unmount();

    renderDetail(QUARANTINE_CAPABILITIES, { isArchived: true });
    expect(await screen.findByText(alerts.quarantinedTitle)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.release })).toBeNull();
  });

  it("lists the quarantine history on the History tab", async () => {
    respondWithCase(buildTestCaseDetail(), QUARANTINE_EVENTS);
    renderDetail(QUARANTINE_CAPABILITIES, { initialTab: TestCaseDetailTab.HISTORY });

    const section = await screen.findByRole("region", { name: history.title });
    const items = within(section).getAllByRole("listitem");
    expect(items).toHaveLength(3);
    expect(within(items[0]).getByText(history.autoReleased)).toBeInTheDocument();
    expect(
      within(items[1]).getByText(interpolate(history.quarantined, { name: "Quinn Tester" })),
    ).toBeInTheDocument();
    expect(
      within(items[1]).getByText(
        interpolate(history.reason, { reason: "Payment sandbox times out" }),
      ),
    ).toBeInTheDocument();
    expect(
      within(items[2]).getByText(interpolate(history.released, { name: history.formerMember })),
    ).toBeInTheDocument();
  });

  it("shows no quarantine history for a case that was never quarantined", async () => {
    renderDetail(QUARANTINE_CAPABILITIES, { initialTab: TestCaseDetailTab.HISTORY });

    await waitFor(() => {
      expect(apiGet).toHaveBeenCalledWith(QUARANTINE_EVENTS_PATH, expect.anything());
    });
    expect(screen.queryByRole("region", { name: history.title })).toBeNull();
  });
});
