import englishDataRows from "@/lib/i18n/locales/en/dataRows.json";
import { createSuccessResult, respondWithRoutes } from "@/modules/auth/test/utils/api-result.util";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { RunDetailPage } from "./run-detail";
import { apiGet } from "./test/mocks/api-client.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { RUN_ID, createRunCase, createRunDetail, createStepResult } from "./test/utils/run.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { RunDetailTab } from "./typing/enums/run-detail-tab.enum";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";

const { iteration } = englishDataRows;

const STEP = createStepResult({
  order: 1,
  action: "Sign in as {{param.email}}",
  expected: "The {{param.role}} dashboard shows",
  status: null,
  actualResult: null,
});

const buildResult = (status: "passed" | "failed", iterationIndex: number) => {
  return {
    id: `d6200000-0000-4000-8000-00000000010${iterationIndex}`,
    status,
    durationMs: 2000,
    suspectedCause: status === "failed" ? ("app_bug" as const) : null,
    causeReason: status === "failed" ? "The QC role sees the admin menu" : null,
    recordedAt: "2026-10-20T10:01:00Z",
    iteration: iterationIndex,
  };
};

const DATA_CASE = createRunCase({
  code: "TC-5",
  title: "Sign in by role",
  result: buildResult("failed", 1),
  steps: [STEP],
  parameters: ["email", "role"],
  iterations: [
    {
      iteration: 0,
      values: { email: "ann@shop.test", role: "admin" },
      result: buildResult("passed", 0),
      steps: [{ ...STEP, status: "passed", actualResult: "Shown" }],
    },
    {
      iteration: 1,
      values: { email: "{{data.qc_email}}", role: "qc" },
      result: buildResult("failed", 1),
      steps: [{ ...STEP, status: "failed", actualResult: "The admin menu shows" }],
    },
    {
      iteration: 2,
      values: { email: "viewer@shop.test", role: "viewer" },
      result: null,
      steps: [STEP],
    },
  ],
});

describe("RunDetailPage with a data-driven case", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    respondWithRoutes(apiGet, {
      [RUN_PATH]: createSuccessResult(
        createRunDetail({
          status: "running",
          finishedAt: null,
          cases: [DATA_CASE],
          data: [{ key: "qc_email", kind: "variable", value: "quinn@shop.test" }],
        }),
      ),
    });
  });

  it("shows one block per iteration with its values, status and steps", async () => {
    const { container } = renderWithProject(
      <RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.RESULTS} />,
    );

    const caseItem = (await screen.findByRole("link", { name: "TC-5" })).closest("li");
    if (caseItem === null) {
      throw new Error("The case is listed.");
    }
    const card = within(caseItem);
    expect(card.getByText("2 of 3 iterations recorded")).toBeInTheDocument();

    const iterations = card.getByRole("list", { name: "Iterations of TC-5" });
    const blocks = within(iterations).getAllByRole("listitem", { name: /^Iteration/ });
    expect(blocks).toHaveLength(3);

    const [first, second, third] = blocks.map((block) => within(block));
    expect(first?.getAllByText("Passed").length).toBeGreaterThan(0);
    expect(first?.queryByText("Failed")).toBeNull();
    expect(first?.getByText("Sign in as ann@shop.test")).toBeInTheDocument();
    expect(first?.getByText("The admin dashboard shows")).toBeInTheDocument();

    expect(second?.getAllByText("Failed").length).toBeGreaterThan(0);
    expect(second?.getByText("The QC role sees the admin menu")).toBeInTheDocument();
    expect(second?.getByText("The admin menu shows")).toBeInTheDocument();
    expect(second?.getAllByText("quinn@shop.test").length).toBeGreaterThan(0);

    expect(third?.getAllByText("Pending").length).toBeGreaterThan(0);
    expect(third?.queryByText("Passed")).toBeNull();
    expect(third?.getByText("viewer")).toBeInTheDocument();
    expect(
      within(blocks[2] as HTMLElement).getByRole("list", {
        name: iteration.stepsLabel.replace("{{code}}", "TC-5").replace("{{number}}", "3"),
      }),
    ).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("hides and shows the iteration blocks with the steps toggle", async () => {
    const user = userEvent.setup();
    renderWithProject(<RunDetailPage runId={RUN_ID} initialTab={RunDetailTab.RESULTS} />);

    expect(await screen.findByRole("list", { name: "Iterations of TC-5" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Hide steps" }));

    expect(screen.queryByRole("list", { name: "Iterations of TC-5" })).not.toBeInTheDocument();
  });
});
