import englishManualRun from "@/lib/i18n/locales/en/manualRun.json";
import englishSuites from "@/lib/i18n/locales/en/suites.json";
import {
  SUITE_ID,
  buildSuiteCase,
  buildSuiteDetail,
  buildSuiteSummary,
} from "@/modules/suites/test/utils/suite.fixture";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { NewManualRunPage } from "./new-manual-run";
import { apiGet, apiPost } from "./test/mocks/api-client.mock";
import { routerReplace } from "./test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  NEW_RUN_ID,
  STAGING_ID,
  buildCreatedRun,
  buildEnvironment,
  buildRunProject,
  buildStory,
} from "./test/utils/run.fixture";
import { openSelectListbox } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const STORIES_PATH = "/api/projects/{project_key}/stories";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const SUITES_PATH = "/api/projects/{project_key}/suites";
const SUITE_PATH = "/api/projects/{project_key}/suites/{suite_id}";
const RUNS_PATH = "/api/projects/{project_key}/runs";

const { manualRun } = englishSuites;
const newText = englishManualRun.new;

const SUITE = buildSuiteDetail({
  cases: [
    buildSuiteCase(),
    buildSuiteCase({
      testCaseId: "5d000000-0000-4000-8000-000000000002",
      code: "TC-2",
      title: "Refund an order",
      storyJiraKey: "SHOP-2",
      position: 1,
    }),
    buildSuiteCase({
      testCaseId: "5d000000-0000-4000-8000-000000000003",
      code: "TC-3",
      title: "Pay with a voucher",
      isNeedingReview: true,
      isRunnable: false,
      position: 2,
    }),
  ],
});

const readPostBody = (): unknown => {
  const [, options] = apiPost.mock.calls[0] ?? [];

  return (options as { body: unknown } | undefined)?.body;
};

const renderPage = (
  initialSuiteId: string | null = SUITE_ID,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <NewManualRunPage initialStoryKey={null} initialSuiteId={initialSuiteId} />,
    buildRunProject(),
  );
};

describe("NewManualRunPage with a suite", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    routerReplace.mockReset();
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([buildStory()]),
      [ENVIRONMENTS_PATH]: createSuccessResult([buildEnvironment()]),
      [SUITES_PATH]: createSuccessResult([buildSuiteSummary()]),
      [SUITE_PATH]: createSuccessResult(SUITE),
    });
    respondWithRoutes(apiPost, {
      [RUNS_PATH]: createCreatedResult(buildCreatedRun({ storyId: null, testSuiteId: SUITE_ID })),
    });
  });

  it("offers the suite's runnable cases and lists the ones it will skip", async () => {
    const { container } = renderPage();

    expect(
      await screen.findByRole("checkbox", { name: "TC-1 · Pay with a valid card · SHOP-1" }),
    ).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "TC-2 · Refund an order · SHOP-2" })).toBeChecked();
    expect(screen.queryByRole("checkbox", { name: /^TC-3/ })).toBeNull();
    expect(screen.getByText("1 case will be skipped")).toBeInTheDocument();
    expect(screen.getByText("TC-3 · Pay with a voucher: Needs review")).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: manualRun.targetSuite })).toBeChecked();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("starts a run of the whole suite without a case list so skipped cases are kept", async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByRole("checkbox", { name: /^TC-1 · / });

    await user.click(screen.getByRole("button", { name: newText.start }));

    await waitFor(() => {
      expect(readPostBody()).toEqual({ suiteId: SUITE_ID, environmentId: STAGING_ID });
    });
    expect(routerReplace).toHaveBeenCalledWith(`/projects/SHOP/runs/${NEW_RUN_ID}/record`);
  });

  it("sends the chosen cases when some are left out", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("checkbox", { name: /^TC-1 · / }));
    await user.click(screen.getByRole("button", { name: newText.start }));

    await waitFor(() => {
      expect(readPostBody()).toEqual({
        suiteId: SUITE_ID,
        environmentId: STAGING_ID,
        testCaseIds: ["5d000000-0000-4000-8000-000000000002"],
      });
    });
  });

  it("switches from a story to a suite picked from the list", async () => {
    const user = userEvent.setup();
    renderPage(null);

    await user.click(await screen.findByRole("radio", { name: manualRun.targetSuite }));
    const listbox = await openSelectListbox(user, /^Suite/);
    await user.click(
      within(listbox).getByRole("option", { name: "Checkout regression", hidden: true }),
    );

    expect(
      await screen.findByRole("checkbox", { name: "TC-1 · Pay with a valid card · SHOP-1" }),
    ).toBeInTheDocument();
  });

  it("names a preselected suite that is not in the list by its name, never its id", async () => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([]),
      [ENVIRONMENTS_PATH]: createSuccessResult([buildEnvironment()]),
      [SUITES_PATH]: createSuccessResult([]),
      [SUITE_PATH]: createSuccessResult(SUITE),
    });
    renderPage();

    const suiteSelect = screen.getByRole("combobox", { name: /^Suite/ });
    await waitFor(() => {
      expect(suiteSelect).toHaveValue("Checkout regression");
    });
    expect(suiteSelect).not.toHaveValue(SUITE_ID);
  });

  it("blocks the start while the suite has a running run", async () => {
    respondWithRoutes(apiGet, {
      [STORIES_PATH]: createSuccessResult([]),
      [ENVIRONMENTS_PATH]: createSuccessResult([buildEnvironment()]),
      [SUITES_PATH]: createSuccessResult([buildSuiteSummary()]),
      [SUITE_PATH]: createSuccessResult({
        ...SUITE,
        runningRun: {
          id: NEW_RUN_ID,
          status: "running",
          startedAt: "2026-11-02T09:00:00Z",
          finishedAt: null,
        },
      }),
    });
    renderPage();

    expect(await screen.findByText(manualRun.runningTitle)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: newText.start })).toBeDisabled();
  });

  it("explains open gaps on the suite's stories", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, { [RUNS_PATH]: createErrorResult(409, "OPEN_GAPS_BLOCK_RUN") });
    renderPage();
    await screen.findByRole("checkbox", { name: /^TC-1 · / });

    await user.click(screen.getByRole("button", { name: newText.start }));

    expect(await screen.findByText(manualRun.errors.openGaps)).toBeInTheDocument();
    expect(routerReplace).not.toHaveBeenCalled();
  });
});
