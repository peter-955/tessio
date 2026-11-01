import { VIEWER_CAPABILITIES } from "@/components/project-context/test/utils/project-fixture.util";
import englishManualRun from "@/lib/i18n/locales/en/manualRun.json";
import type { UploadedFile } from "@/lib/uploads/typing/types/uploaded-file.type";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { RecordManualRunPage } from "./record-manual-run";
import { apiGet, apiPost, apiPut } from "./test/mocks/api-client.mock";
import { routerPush } from "./test/mocks/next-navigation.mock";
import { EVIDENCE_FILE_ID, buildEvidenceFile, uploadFile } from "./test/mocks/signed-upload.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "./test/utils/api-result.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  OTHER_USER_ID,
  RUN_ID,
  buildRecordedResult,
  buildRun,
  buildRunCase,
  buildRunProject,
  buildStep,
} from "./test/utils/run.fixture";
import { chooseSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { ManualRun } from "./typing/types/manual-run.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("./test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("@/lib/uploads/hooks/use-signed-upload", async () => {
  return (await import("./test/mocks/signed-upload.mock")).signedUploadMock;
});

const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";
const CASE_RESULT_PATH = "/api/projects/{project_key}/runs/{run_id}/cases/{test_case_id}";
const FINISH_PATH = "/api/projects/{project_key}/runs/{run_id}/finish";

const { errors, evidence, finish, record, status } = englishManualRun;

let currentRun: ManualRun = buildRun();

const recordedFirstCase = (): ManualRun => {
  const [firstCase, ...otherCases] = buildRun().cases;

  return buildRun({
    cases: [
      buildRunCase({
        ...firstCase,
        result: buildRecordedResult("failed"),
        steps: [
          buildStep({ order: 1, status: "passed", actualResult: "Opened" }),
          buildStep({
            order: 2,
            action: "Pay by card",
            status: "failed",
            actualResult: "Declined",
            error: "Card refused",
            evidenceFileId: EVIDENCE_FILE_ID,
          }),
        ],
      }),
      ...otherCases,
    ],
  });
};

const renderPage = (
  project = buildRunProject(),
  runId = RUN_ID,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<RecordManualRunPage runId={runId} />, project);
};

const chooseStepStatus = async (
  user: UserEvent,
  order: number,
  statusLabel: string,
): Promise<void> => {
  const group = await screen.findByRole("radiogroup", { name: `Step ${order} status` });
  await user.click(within(group).getByRole("radio", { name: statusLabel }));
};

const readPutBody = (): unknown => {
  const [, options] = apiPut.mock.calls[0] ?? [];

  return (options as { body: unknown } | undefined)?.body;
};

const findCurrentCaseHeading = (name: string): Promise<HTMLElement> => {
  return screen.findByRole("heading", { name });
};

describe("RecordManualRunPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    currentRun = buildRun();
    respondWithRoutes(apiGet, {
      [RUN_PATH]: () => {
        return createSuccessResult(currentRun);
      },
    });
    respondWithRoutes(apiPut, {
      [CASE_RESULT_PATH]: () => {
        currentRun = recordedFirstCase();

        return createSuccessResult({});
      },
    });
    respondWithRoutes(apiPost, { [FINISH_PATH]: createSuccessResult({}) });
  });

  it("shows the run header, the case list and the live suggestion", async () => {
    const user = userEvent.setup();
    const { container } = renderPage();

    expect(await screen.findByRole("heading", { name: "Manual run · SHOP-1" })).toBeInTheDocument();
    expect(screen.getByText("Staging · Started by Quinn QC")).toBeInTheDocument();
    expect(screen.getByText("0 of 2 cases recorded")).toBeInTheDocument();
    const navigation = screen.getByRole("navigation", { name: record.caseList });
    expect(within(navigation).getByRole("button", { name: /^TC-1/ })).toHaveAttribute(
      "aria-current",
      "true",
    );
    expect(within(navigation).getAllByText(record.notRecorded)).toHaveLength(2);
    expect(screen.getByText("Suggested: Skipped")).toBeInTheDocument();

    await chooseStepStatus(user, 1, status.passed);
    expect(screen.getByText("Suggested: Passed")).toBeInTheDocument();
    await chooseStepStatus(user, 2, status.failed);
    expect(screen.getByText("Suggested: Failed")).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: record.error })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("sends the override, then moves on to the next unrecorded case", async () => {
    const user = userEvent.setup();
    renderPage();

    await chooseStepStatus(user, 1, status.passed);
    await user.type(
      screen.getAllByRole("textbox", { name: record.actualResult })[0] as HTMLElement,
      " Opened ",
    );
    await chooseSelectOption(user, new RegExp(`^${record.caseResult}`), status.blocked);
    await user.click(screen.getByRole("button", { name: record.save }));

    expect(await findCurrentCaseHeading("TC-2 · Pay by voucher")).toBeInTheDocument();
    expect(readPutBody()).toEqual({
      status: "blocked",
      durationMs: null,
      steps: [
        { order: 1, status: "passed", actualResult: "Opened", error: null, evidenceFileId: null },
      ],
    });
    expect(apiPut).toHaveBeenCalledWith(
      CASE_RESULT_PATH,
      expect.objectContaining({
        params: {
          path: {
            project_key: "SHOP",
            run_id: RUN_ID,
            test_case_id: buildRun().cases[0]?.testCaseId,
          },
        },
      }),
    );
    expect(screen.getByText("1 of 2 cases recorded")).toBeInTheDocument();
  });

  it("blocks saving while evidence uploads and sends the evidence id", async () => {
    let resolveUpload: (file: UploadedFile) => void = () => {
      return;
    };
    uploadFile.mockImplementation(() => {
      return new Promise<UploadedFile>((resolve) => {
        resolveUpload = resolve;
      });
    });
    const user = userEvent.setup();
    const { container } = renderPage();

    await chooseStepStatus(user, 1, status.failed);
    const file = new File(["image"], "cart.png", { type: "image/png" });
    const [fileInput] = container.querySelectorAll<HTMLInputElement>('input[type="file"]');
    await user.upload(fileInput as HTMLInputElement, file);

    expect(await screen.findByText("Uploading 0%")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: evidence.cancel })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: record.save })).toBeDisabled();

    resolveUpload(buildEvidenceFile(file));
    expect(await screen.findByText("cart.png")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: evidence.remove })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: record.save })).toBeEnabled();

    await user.click(screen.getByRole("button", { name: record.save }));
    await waitFor(() => {
      expect(readPutBody()).toEqual({
        status: null,
        durationMs: null,
        steps: [
          {
            order: 1,
            status: "failed",
            actualResult: "",
            error: null,
            evidenceFileId: EVIDENCE_FILE_ID,
          },
        ],
      });
    });
  });

  it("removes an uploaded evidence file", async () => {
    uploadFile.mockImplementation((file) => {
      return Promise.resolve(buildEvidenceFile(file));
    });
    const user = userEvent.setup();
    const { container } = renderPage();

    await chooseStepStatus(user, 1, status.passed);
    const [fileInput] = container.querySelectorAll<HTMLInputElement>('input[type="file"]');
    await user.upload(
      fileInput as HTMLInputElement,
      new File(["a"], "cart.png", { type: "image/png" }),
    );
    await user.click(await screen.findByRole("button", { name: evidence.remove }));

    expect(screen.queryByText("cart.png")).not.toBeInTheDocument();
  });

  it("shows a recorded case read-only", async () => {
    currentRun = recordedFirstCase();
    const user = userEvent.setup();
    renderPage();

    const navigation = await screen.findByRole("navigation", { name: record.caseList });
    await user.click(within(navigation).getByRole("button", { name: /^TC-1/ }));

    expect(await findCurrentCaseHeading("TC-1 · Pay by card")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: record.save })).not.toBeInTheDocument();
    expect(screen.queryByRole("radiogroup")).not.toBeInTheDocument();
    expect(screen.getByText(record.evidenceAttached)).toBeInTheDocument();
    expect(screen.getByText(`${record.error}: Card refused`)).toBeInTheDocument();
  });

  it("shows the CASE_RESULT_EXISTS message", async () => {
    respondWithRoutes(apiPut, { [CASE_RESULT_PATH]: createErrorResult(409, "CASE_RESULT_EXISTS") });
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("button", { name: record.save }));

    expect(await screen.findByText(errors.resultExists)).toBeInTheDocument();
  });

  it("selects the Finish button once every case is recorded", async () => {
    currentRun = buildRun({ cases: [buildRun().cases[0] ?? buildRunCase()] });
    respondWithRoutes(apiPut, {
      [CASE_RESULT_PATH]: () => {
        currentRun = buildRun({ cases: [recordedFirstCase().cases[0] ?? buildRunCase()] });

        return createSuccessResult({});
      },
    });
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("button", { name: record.save }));

    expect(await screen.findByText(record.allRecorded)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: finish.action })).toHaveFocus();
  });

  it("finishes the run with a summary and opens the run detail", async () => {
    currentRun = recordedFirstCase();
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("button", { name: finish.action }));
    const dialog = await screen.findByRole("dialog", { name: finish.title });
    expect(within(dialog).getByText(finish.unrecorded_one.replace("{{count}}", "1"))).toBeVisible();
    await user.type(
      within(dialog).getByRole("textbox", { name: finish.summary }),
      "  Card flow broken ",
    );
    await user.click(within(dialog).getByRole("button", { name: finish.confirm }));

    await waitFor(() => {
      expect(routerPush).toHaveBeenCalledWith(`/projects/SHOP/runs/${RUN_ID}`);
    });
    expect(apiPost).toHaveBeenCalledWith(
      FINISH_PATH,
      expect.objectContaining({ body: { summary: "Card flow broken" } }),
    );
  });

  it("warns that finishing without results aborts the run", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByRole("button", { name: finish.action }));
    const dialog = await screen.findByRole("dialog", { name: finish.title });

    expect(within(dialog).getByText(finish.noResults)).toBeInTheDocument();
  });

  it("explains a finished run", async () => {
    currentRun = buildRun({ status: "passed" });
    renderPage();

    expect(await screen.findByText(record.runFinished)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: record.openDetail })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs/${RUN_ID}`,
    );
    expect(screen.queryByRole("button", { name: record.save })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: finish.action })).not.toBeInTheDocument();
  });

  it("explains a Claude run", async () => {
    currentRun = buildRun({ executor: "claude" });
    renderPage();

    expect(await screen.findByText(record.claudeRun)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: record.save })).not.toBeInTheDocument();
  });

  it("shows somebody else's run read-only", async () => {
    currentRun = buildRun({ startedBy: OTHER_USER_ID, startedByName: "Robin Rivera" });
    renderPage();

    expect(await screen.findByText("Only Robin Rivera can record this run.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: record.save })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: finish.action })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "TC-1 · Pay by card" })).toBeInTheDocument();
  });

  it("shows a viewer the run read-only", async () => {
    renderPage(buildRunProject({ capabilities: VIEWER_CAPABILITIES }));

    expect(await screen.findByText("Only Quinn QC can record this run.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: record.save })).not.toBeInTheDocument();
  });

  it("shows a missing run", async () => {
    respondWithRoutes(apiGet, { [RUN_PATH]: createErrorResult(404, "NOT_FOUND") });
    renderPage();

    expect(await screen.findByText(record.notFound)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: record.backToRuns, hidden: false }),
    ).toBeInTheDocument();
  });

  it("shows a missing run for a malformed id without asking the server", async () => {
    respondWithRoutes(apiGet, {});
    renderPage(buildRunProject(), "not-a-run");

    expect(await screen.findByText(record.notFound)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalledWith(RUN_PATH, expect.anything());
  });
});
