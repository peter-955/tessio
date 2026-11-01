import englishRuns from "@/lib/i18n/locales/en/runs.json";
import { setNavigation } from "@/modules/auth/test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "@/modules/auth/test/utils/api-result.util";
import type { RunCase } from "@/shared/typing/types/test-run.type";
import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { GET_RUN_KEY } from "./hooks/queries/use-get-run";
import { RunDetailPage } from "./run-detail";
import { apiGet } from "./test/mocks/api-client.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  CHILD_RUN_ID,
  EVIDENCE_FILE_ID,
  PARENT_RUN_ID,
  RUN_ID,
  SCREENSHOT_FILE_ID,
  createRunCase,
  createRunDetail,
  createStepResult,
} from "./test/utils/run.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { RunDetailTab } from "./typing/enums/run-detail-tab.enum";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface FileRequest {
  params: { path: { file_id: string } };
}

const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";
const FILE_PATH = "/api/projects/{project_key}/files/{file_id}";
const SCREENSHOT_URL = "https://files.example.test/screenshot.png";
const EVIDENCE_URL = "https://files.example.test/evidence.pdf";

const { abortReason, detail, notFound, report, screenshot } = englishRuns;

const PASSED_CASE = createRunCase();

const FAILED_CASE = createRunCase({
  testCaseId: "d6000000-0000-4000-8000-000000000002",
  code: "TC-2",
  title: "Decline an expired card",
  versionNumber: 1,
  position: 2,
  result: {
    id: "d6200000-0000-4000-8000-000000000002",
    status: "failed",
    durationMs: 9000,
    recordedAt: "2026-10-20T10:01:30Z",
  },
  steps: [
    createStepResult({ order: 1, action: "Enter an expired card" }),
    createStepResult({
      order: 2,
      action: "Pay",
      expected: "A decline message",
      status: "failed",
      actualResult: "The order was placed",
      error: "AssertionError: expected a decline",
      screenshotFileId: SCREENSHOT_FILE_ID,
      screenshotStatus: "pending",
      evidenceFileId: EVIDENCE_FILE_ID,
    }),
  ],
});

const UNREPORTED_CASE = createRunCase({
  testCaseId: "d6000000-0000-4000-8000-000000000003",
  code: "TC-3",
  title: "Pay in instalments",
  position: 3,
  result: null,
  steps: [createStepResult({ status: null, actualResult: null })],
});

const buildPendingCase = (index: number): RunCase => {
  return createRunCase({
    testCaseId: `d6000000-0000-4000-8000-00000000010${String(index)}`,
    code: `TC-1${String(index)}`,
    title: `Pending case ${String(index)}`,
    position: 10 + index,
    result: null,
  });
};

const FINISHED_RUN = createRunDetail({
  childRunIds: [CHILD_RUN_ID],
  parentRunId: PARENT_RUN_ID,
  cases: [PASSED_CASE, FAILED_CASE, UNREPORTED_CASE],
  report: {
    counts: { total: 3, passed: 1, failed: 1, blocked: 0, skipped: 0, notReported: 1 },
    failedCases: [
      {
        testCaseId: FAILED_CASE.testCaseId,
        code: "TC-2",
        title: "Decline an expired card",
        status: "failed",
        stepOrder: 2,
        stepAction: "Pay",
        actualResult: "The order was placed",
        error: "AssertionError: expected a decline",
      },
    ],
    criterionImpacts: [
      {
        criterionId: "c7000000-0000-4000-8000-000000000001",
        code: "AC-1",
        text: "A valid card is charged",
        status: "passed",
        runCaseCodes: ["TC-1"],
        failedCaseCodes: [],
      },
      {
        criterionId: "c7000000-0000-4000-8000-000000000002",
        code: "AC-2",
        text: "An expired card is declined",
        status: "failed",
        runCaseCodes: ["TC-2"],
        failedCaseCodes: ["TC-2"],
      },
      {
        criterionId: "c7000000-0000-4000-8000-000000000003",
        code: "AC-3",
        text: "Instalments are offered",
        status: "uncovered",
        runCaseCodes: [],
        failedCaseCodes: [],
      },
    ],
    missingScreenshots: [
      {
        caseResultId: "d6200000-0000-4000-8000-000000000002",
        testCaseId: FAILED_CASE.testCaseId,
        code: "TC-2",
        stepOrder: 2,
      },
    ],
    summary: "Checkout fails when paying by card.",
    builtAt: "2026-10-20T10:02:05Z",
  },
});

const RUNNING_RUN = createRunDetail({
  status: "running",
  finishedAt: null,
  summary: null,
  report: null,
  cases: [PASSED_CASE, FAILED_CASE, buildPendingCase(1), buildPendingCase(2), buildPendingCase(3)],
});

const respondWithRun = (run: ApiResult | (() => ApiResult)): void => {
  respondWithRoutes(apiGet, {
    [RUN_PATH]: run,
    [FILE_PATH]: createSuccessResult({
      url: SCREENSHOT_URL,
      expiresAt: "2026-10-20T10:07:00Z",
    }),
  });
};

const renderPage = (
  runId = RUN_ID,
  initialTab = RunDetailTab.RESULTS,
  actionLabel: string | null = null,
) => {
  return renderWithProject(
    <RunDetailPage
      runId={runId}
      initialTab={initialTab}
      actions={actionLabel === null ? undefined : <button type="button">{actionLabel}</button>}
    />,
  );
};

const findCase = async (code: string): Promise<HTMLElement> => {
  const link = await screen.findByRole("link", { name: code });

  return link.closest("li") as HTMLElement;
};

const countRequests = (path: string): number => {
  return apiGet.mock.calls.filter(([calledPath]) => calledPath === path).length;
};

describe("RunDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    setNavigation(`/projects/APP/runs/${RUN_ID}`);
    respondWithRun(createSuccessResult(FINISHED_RUN));
  });

  it("renders the header, details, lineage and every case with its badge", async () => {
    renderPage();

    expect(await screen.findByRole("heading", { name: "Run on APP-1" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "APP-1" })).toHaveAttribute(
      "href",
      "/projects/APP/stories/APP-1?tab=runs",
    );
    expect(screen.getByRole("link", { name: "Re-run of an earlier run" })).toHaveAttribute(
      "href",
      `/projects/APP/runs/${PARENT_RUN_ID}`,
    );
    expect(screen.getByRole("link", { name: "Re-run 1" })).toHaveAttribute(
      "href",
      `/projects/APP/runs/${CHILD_RUN_ID}`,
    );
    const passedCase = within(await findCase("TC-1"));
    expect(passedCase.getByText("Passed")).toBeInTheDocument();
    expect(passedCase.getByText("v2")).toBeInTheDocument();
    expect(passedCase.getByRole("link", { name: "TC-1" })).toHaveAttribute(
      "href",
      "/projects/APP/test-cases/TC-1",
    );
    const unreportedCase = within(await findCase("TC-3"));
    expect(unreportedCase.getByText("Not reported")).toBeInTheDocument();
    expect(unreportedCase.getByText(detail.notReportedHint)).toBeInTheDocument();
    expect(screen.queryByText(detail.live)).not.toBeInTheDocument();
  });

  it("shows live progress and pending cases while the run is running", async () => {
    respondWithRun(createSuccessResult(RUNNING_RUN));
    renderPage();

    expect(await screen.findByText(detail.live)).toBeInTheDocument();
    expect(screen.getByText("2 of 5 cases reported")).toBeInTheDocument();
    expect(screen.getByText(detail.live).closest("[aria-live]")).toHaveAttribute(
      "aria-live",
      "polite",
    );
    const pendingCase = within(await findCase("TC-11"));
    expect(pendingCase.getByText("Pending")).toBeInTheDocument();
    expect(pendingCase.queryByText(detail.notReportedHint)).not.toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Report" })).toBeDisabled();
  });

  it("starts the failed case expanded and shows an uploading screenshot while running", async () => {
    const user = userEvent.setup();
    respondWithRun(createSuccessResult(RUNNING_RUN));
    renderPage();

    const failedCase = within(await findCase("TC-2"));
    expect(failedCase.getByRole("button", { name: "Hide steps" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    const steps = failedCase.getByRole("list", { name: "Steps of TC-2" });
    expect(within(steps).getAllByRole("listitem")).toHaveLength(2);
    expect(within(steps).getByText("AssertionError: expected a decline")).toBeInTheDocument();
    expect(within(steps).getByText(screenshot.uploading)).toBeInTheDocument();

    const passedCase = within(await findCase("TC-1"));
    const toggle = passedCase.getByRole("button", { name: "Show steps" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(passedCase.queryByRole("list", { name: "Steps of TC-1" })).not.toBeInTheDocument();
    await user.click(toggle);
    expect(passedCase.getByRole("list", { name: "Steps of TC-1" })).toBeInTheDocument();
    expect(countRequests(FILE_PATH)).toBe(0);
  });

  it("shows a pending screenshot as missing once the run has finished", async () => {
    renderPage();

    const failedCase = within(await findCase("TC-2"));
    expect(failedCase.getByText(screenshot.missing)).toBeInTheDocument();
    expect(countRequests(FILE_PATH)).toBe(0);
  });

  it("loads an uploaded screenshot through a signed link and opens evidence", async () => {
    const user = userEvent.setup();
    const openWindow = vi.spyOn(window, "open").mockReturnValue(null);
    const uploadedCase: RunCase = {
      ...FAILED_CASE,
      steps: FAILED_CASE.steps.map((step) => {
        return step.screenshotFileId === null ? step : { ...step, screenshotStatus: "uploaded" };
      }),
    };
    respondWithRoutes(apiGet, {
      [RUN_PATH]: createSuccessResult({ ...FINISHED_RUN, cases: [uploadedCase] }),
      [FILE_PATH]: () => {
        const fileId = (apiGet.mock.lastCall?.[1] as FileRequest).params.path.file_id;

        return createSuccessResult({
          url: fileId === SCREENSHOT_FILE_ID ? SCREENSHOT_URL : EVIDENCE_URL,
          expiresAt: "2026-10-20T10:07:00Z",
        });
      },
    });
    renderPage();

    const image = await screen.findByRole("img", { name: "Screenshot of TC-2 step 2" });
    expect(image).toHaveAttribute("src", SCREENSHOT_URL);
    expect(
      apiGet.mock.calls.some(([path, options]) => {
        return (
          path === FILE_PATH && (options as FileRequest).params.path.file_id === SCREENSHOT_FILE_ID
        );
      }),
    ).toBe(true);

    await user.click(screen.getByRole("button", { name: screenshot.openEvidence }));

    await waitFor(() => {
      expect(openWindow).toHaveBeenCalledWith(EVIDENCE_URL, "_blank", "noopener");
    });
  });

  it("shows a load failure when the screenshot link cannot be signed", async () => {
    const uploadedCase: RunCase = {
      ...FAILED_CASE,
      steps: FAILED_CASE.steps.map((step) => {
        return step.screenshotFileId === null ? step : { ...step, screenshotStatus: "uploaded" };
      }),
    };
    respondWithRoutes(apiGet, {
      [RUN_PATH]: createSuccessResult({ ...FINISHED_RUN, cases: [uploadedCase] }),
      [FILE_PATH]: createErrorResult(404, "NOT_FOUND"),
    });
    renderPage();

    expect(await screen.findByText(screenshot.loadFailed)).toBeInTheDocument();
  });

  it("renders a newly recorded case after a live invalidation", async () => {
    let currentRun = RUNNING_RUN;
    respondWithRun(() => createSuccessResult(currentRun));
    const { queryClient } = renderPage();

    const pendingCase = within(await findCase("TC-11"));
    expect(pendingCase.getByText("Pending")).toBeInTheDocument();

    currentRun = {
      ...RUNNING_RUN,
      cases: RUNNING_RUN.cases.map((runCase) => {
        return runCase.code === "TC-11"
          ? {
              ...runCase,
              result: {
                id: "d6200000-0000-4000-8000-000000000011",
                status: "blocked",
                durationMs: 1000,
                recordedAt: "2026-10-20T10:01:40Z",
              },
            }
          : runCase;
      }),
    };
    await act(async () => {
      await queryClient.invalidateQueries({ queryKey: [GET_RUN_KEY] });
    });

    await waitFor(() => {
      expect(pendingCase.getByText("Blocked")).toBeInTheDocument();
    });
    expect(screen.getByText("3 of 5 cases reported")).toBeInTheDocument();
    expect(pendingCase.getByRole("button", { name: "Hide steps" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
  });

  it("shows the report with the summary, failed cases, criteria impact and missing screenshots", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("tab", { name: "Report" }));

    expect(screen.getByText("Checkout fails when paying by card.")).toBeInTheDocument();
    expect(screen.getByText("3 cases · 1 passed · 1 failed · 1 not reported")).toBeInTheDocument();
    expect(screen.getByText("Failed at step 2: Pay")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "TC-2" })).toHaveAttribute(
      "href",
      `/projects/APP/runs/${RUN_ID}?tab=results#case-TC-2`,
    );
    const criteria = within(screen.getByRole("table", { name: report.criteria }));
    const failedRow = within(criteria.getByText("AC-2").closest("tr") as HTMLElement);
    expect(failedRow.getByText("Failed")).toBeInTheDocument();
    const uncoveredRow = within(criteria.getByText("AC-3").closest("tr") as HTMLElement);
    expect(uncoveredRow.getByText("Not covered")).toBeInTheDocument();
    expect(screen.getByText(report.missingScreenshots)).toBeInTheDocument();
    expect(screen.getByText("TC-2 · step 2")).toBeInTheDocument();
  });

  it("opens on the report tab when asked and shows an aborted run's reason", async () => {
    respondWithRun(
      createSuccessResult({ ...FINISHED_RUN, status: "aborted", abortReason: "no_results" }),
    );
    renderPage(RUN_ID, RunDetailTab.REPORT);

    expect(await screen.findByText("Failed at step 2: Pay")).toBeInTheDocument();
    expect(screen.getByText(abortReason.no_results)).toBeInTheDocument();
  });

  it("shows not found for an invalid id without sending a request", async () => {
    renderPage("not-a-run");

    expect(await screen.findByText(notFound.title)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: notFound.back })).toHaveAttribute(
      "href",
      "/projects/APP/runs",
    );
    expect(apiGet).not.toHaveBeenCalled();
  });

  it("shows not found when the server answers 404", async () => {
    respondWithRun(createErrorResult(404, "NOT_FOUND"));
    renderPage();

    expect(await screen.findByText(notFound.title)).toBeInTheDocument();
  });

  it("renders the actions slot and passes axe", async () => {
    const { container } = renderPage(RUN_ID, RunDetailTab.RESULTS, "Re-run failed");

    expect(await screen.findByRole("button", { name: "Re-run failed" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
