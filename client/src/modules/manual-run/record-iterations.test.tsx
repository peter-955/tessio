import englishDataRows from "@/lib/i18n/locales/en/dataRows.json";
import englishManualRun from "@/lib/i18n/locales/en/manualRun.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { RecordManualRunPage } from "./record-manual-run";
import { apiGet, apiPut } from "./test/mocks/api-client.mock";
import { createSuccessResult, respondWithRoutes } from "./test/utils/api-result.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import {
  RUN_ID,
  buildRecordedResult,
  buildRun,
  buildRunCase,
  buildRunProject,
  buildStep,
} from "./test/utils/run.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { ManualRun, ManualRunCase } from "./typing/types/manual-run.type";

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

const { record, status } = englishManualRun;
const { iteration } = englishDataRows;

const STEP = buildStep({ order: 1, action: "Sign in as {{param.email}}", expected: null });

const buildDataCase = (recordedIterations: readonly number[]): ManualRunCase => {
  const rows = [{ email: "ann@shop.test" }, { email: "bob@shop.test" }];

  return buildRunCase({
    code: "TC-1",
    title: "Sign in",
    steps: [STEP],
    parameters: ["email"],
    result: recordedIterations.length === 0 ? null : buildRecordedResult("passed"),
    iterations: rows.map((values, index) => {
      const isRecorded = recordedIterations.includes(index);

      return {
        iteration: index,
        values,
        result: isRecorded ? { ...buildRecordedResult("passed"), iteration: index } : null,
        steps: [isRecorded ? { ...STEP, status: "passed", actualResult: "Signed in" } : STEP],
      };
    }),
  });
};

const buildDataRun = (recordedIterations: readonly number[]): ManualRun => {
  const run = buildRun();

  return { ...run, cases: [buildDataCase(recordedIterations), ...run.cases.slice(1)] };
};

let currentRun: ManualRun = buildDataRun([]);

const readPutBodies = (): unknown[] => {
  return apiPut.mock.calls.map(([, options]) => (options as { body: unknown }).body);
};

const passStep = async (user: UserEvent): Promise<void> => {
  const group = await screen.findByRole("radiogroup", { name: "Step 1 status" });
  await user.click(within(group).getByRole("radio", { name: status.passed }));
};

describe("RecordManualRunPage with a data-driven case", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    currentRun = buildDataRun([]);
    apiPut.mockReset();
    respondWithRoutes(apiGet, {
      [RUN_PATH]: () => {
        return createSuccessResult(currentRun);
      },
    });
    respondWithRoutes(apiPut, {
      [CASE_RESULT_PATH]: () => {
        currentRun = buildDataRun(apiPut.mock.calls.length === 1 ? [0] : [0, 1]);

        return createSuccessResult({});
      },
    });
  });

  it("records each iteration on its own, then moves to the next case", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProject(
      <RecordManualRunPage runId={RUN_ID} />,
      buildRunProject(),
    );

    const iterations = await screen.findByRole("list", { name: "Iterations of TC-1" });
    const blocks = within(iterations).getAllByRole("listitem", { name: /^Iteration/ });
    expect(blocks).toHaveLength(2);
    expect(screen.getAllByText("0 of 2 iterations recorded").length).toBeGreaterThan(0);
    expect(within(blocks[0] as HTMLElement).getByText("Sign in as ann@shop.test")).toBeVisible();
    expect(
      within(blocks[1] as HTMLElement).getByRole("button", { name: "Record iteration 2" }),
    ).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();

    await passStep(user);
    await user.click(screen.getByRole("button", { name: "Save iteration 1" }));

    expect(await screen.findByText("TC-1, iteration 1 saved.")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Save iteration 2" })).toBeInTheDocument();
    expect(screen.getByText("Sign in as bob@shop.test")).toBeInTheDocument();
    expect(screen.getAllByText("1 of 2 iterations recorded").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Show iteration 1" })).toBeInTheDocument();

    await passStep(user);
    await user.click(screen.getByRole("button", { name: "Save iteration 2" }));

    expect(await screen.findByRole("heading", { name: "TC-2 · Pay by voucher" })).toBeVisible();
    await waitFor(() => {
      expect(readPutBodies()).toEqual([
        {
          status: null,
          durationMs: null,
          iteration: 0,
          steps: [
            { order: 1, status: "passed", actualResult: "", error: null, evidenceFileId: null },
          ],
        },
        {
          status: null,
          durationMs: null,
          iteration: 1,
          steps: [
            { order: 1, status: "passed", actualResult: "", error: null, evidenceFileId: null },
          ],
        },
      ]);
    });
    expect(screen.queryByText(iteration.recordHint)).toBeNull();
  });

  it("counts a data-driven case as recorded only when every iteration is", async () => {
    currentRun = buildDataRun([0]);
    renderWithProject(<RecordManualRunPage runId={RUN_ID} />, buildRunProject());

    expect(await screen.findByText("Started by Quinn QC · 0 of 2 cases recorded")).toBeVisible();
    const navigation = screen.getByRole("navigation", { name: record.caseList });
    expect(within(navigation).getByRole("button", { name: /^TC-1/ })).toHaveTextContent(
      "1 of 2 iterations recorded",
    );
    expect(await screen.findByRole("button", { name: "Save iteration 2" })).toBeInTheDocument();
  });
});
