import englishSuites from "@/lib/i18n/locales/en/suites.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SuiteDetailPage } from "./suite-detail";
import { apiGet, apiPatch, apiPost, apiPut } from "./test/mocks/api-client.mock";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import { QC_PROJECT, VIEWER_PROJECT } from "./test/utils/suite-project.util";
import {
  CASE_IDS,
  RUN_ID,
  SUITE_ID,
  buildSuiteDetail,
  reorderSuiteCases,
} from "./test/utils/suite.fixture";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface CasesRequest {
  params: { path: { project_key: string; suite_id: string } };
  body: { testCaseIds: string[] };
}

const SUITE_PATH = "/api/projects/{project_key}/suites/{suite_id}";
const CASES_PATH = "/api/projects/{project_key}/suites/{suite_id}/cases";
const ARCHIVE_PATH = "/api/projects/{project_key}/suites/{suite_id}/archive";

const { archive, cases, command, detail, form, toasts } = englishSuites;

const readCodes = (): string[] => {
  return within(screen.getByRole("list", { name: cases.listLabel }))
    .getAllByRole("listitem")
    .map((item) => {
      return within(item).getAllByRole("link")[0].textContent ?? "";
    });
};

const readPutCaseIds = (): string[][] => {
  return apiPut.mock.calls.map(([, options]) => (options as CasesRequest).body.testCaseIds);
};

const openCaseMenu = async (user: UserEvent, code: string): Promise<void> => {
  await user.click(
    screen.getByRole("button", { name: cases.actionsFor.replace("{{code}}", code) }),
  );
};

const renderDetail = (
  project = QC_PROJECT,
  suiteId: string = SUITE_ID,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<SuiteDetailPage suiteId={suiteId} />, project);
};

describe("SuiteDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    apiPost.mockReset();
    apiPatch.mockReset();
    respondWithRoutes(apiGet, { [SUITE_PATH]: createSuccessResult(buildSuiteDetail()) });
    apiPut.mockImplementation((_path, options) => {
      const caseIds = (options as CasesRequest).body.testCaseIds;

      return Promise.resolve(
        createSuccessResult(
          buildSuiteDetail({ cases: reorderSuiteCases(caseIds), caseCount: caseIds.length }),
        ),
      );
    });
  });

  it("shows the suite, its cases in order and the Claude command", async () => {
    const { container } = renderDetail();

    expect(await screen.findByRole("heading", { name: "Checkout regression" })).toBeInTheDocument();
    expect(screen.getByText("Everything a buyer does at the till.")).toBeInTheDocument();
    expect(screen.getByText("3 cases · 2 ready to run")).toBeInTheDocument();
    expect(readCodes()).toEqual(["TC-1", "TC-2", "TC-3"]);
    const draftRow = screen.getAllByRole("listitem")[2];
    expect(within(draftRow).getByText("SHOP-1 · Pay by card")).toBeInTheDocument();
    expect(within(draftRow).getByText(cases.skipped)).toBeInTheDocument();
    expect(screen.getByText(command.title)).toBeInTheDocument();
    expect(screen.getByText('/tessio:run-suite "Checkout regression"')).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.startManualRun })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs/new?suite=${SUITE_ID}`,
    );
    expect(screen.getByRole("link", { name: detail.viewRuns })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs?suite=${SUITE_ID}`,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("saves the new order when a case is dragged by its handle", async () => {
    renderDetail();
    await screen.findByRole("list", { name: cases.listLabel });
    const items = screen.getAllByRole("listitem");
    const dataTransfer = { setData: vi.fn(), effectAllowed: "none", dropEffect: "none" };

    fireEvent.pointerDown(screen.getByRole("button", { name: "Reorder TC-3" }));
    fireEvent.dragStart(items[2], { dataTransfer });
    fireEvent.dragOver(items[0], { dataTransfer });
    fireEvent.drop(items[0], { dataTransfer });

    expect(readCodes()).toEqual(["TC-3", "TC-1", "TC-2"]);
    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledWith(CASES_PATH, {
        params: { path: { project_key: "SHOP", suite_id: SUITE_ID } },
        body: { testCaseIds: [CASE_IDS[2], CASE_IDS[0], CASE_IDS[1]] },
      });
    });
  });

  it("moves a case with the arrow keys and sends each order in turn", async () => {
    const user = userEvent.setup();
    renderDetail();
    await screen.findByRole("list", { name: cases.listLabel });

    screen.getByRole("button", { name: "Reorder TC-1" }).focus();
    await user.keyboard("{ArrowDown}");
    expect(readCodes()).toEqual(["TC-2", "TC-1", "TC-3"]);
    await user.keyboard("{ArrowDown}");

    expect(readCodes()).toEqual(["TC-2", "TC-3", "TC-1"]);
    await waitFor(() => {
      expect(readPutCaseIds().at(-1)).toEqual([CASE_IDS[1], CASE_IDS[2], CASE_IDS[0]]);
    });
    expect(screen.getByRole("button", { name: "Reorder TC-1" })).toHaveFocus();
  });

  it("moves a case to the bottom and removes a case from its menu", async () => {
    const user = userEvent.setup();
    renderDetail();
    await screen.findByRole("list", { name: cases.listLabel });

    await openCaseMenu(user, "TC-1");
    await user.click(await screen.findByRole("menuitem", { name: cases.moveToBottom }));
    await waitFor(() => {
      expect(readPutCaseIds()).toEqual([[CASE_IDS[1], CASE_IDS[2], CASE_IDS[0]]]);
    });

    await openCaseMenu(user, "TC-3");
    await user.click(await screen.findByRole("menuitem", { name: cases.remove }));

    await waitFor(() => {
      expect(readPutCaseIds().at(-1)).toEqual([CASE_IDS[1], CASE_IDS[0]]);
    });
    expect(await screen.findByText("TC-3 removed from the suite")).toBeInTheDocument();
    expect(readCodes()).toEqual(["TC-2", "TC-1"]);
  });

  it("says a case was removed only once the save succeeds", async () => {
    const user = userEvent.setup();
    let resolveSave: (result: ReturnType<typeof createErrorResult>) => void = () => undefined;
    apiPut.mockImplementation(() => {
      return new Promise((resolve) => {
        resolveSave = resolve;
      });
    });
    renderDetail();
    await screen.findByRole("list", { name: cases.listLabel });

    await openCaseMenu(user, "TC-2");
    await user.click(await screen.findByRole("menuitem", { name: cases.remove }));

    await waitFor(() => {
      expect(readPutCaseIds()).toEqual([[CASE_IDS[0], CASE_IDS[2]]]);
    });
    expect(screen.queryByText("TC-2 removed from the suite")).toBeNull();

    resolveSave(createErrorResult(404, "UNKNOWN_REFERENCE"));

    expect(await screen.findByText(englishSuites.errors.unknownReference)).toBeInTheDocument();
    expect(screen.queryByText("TC-2 removed from the suite")).toBeNull();
    expect(readCodes()).toEqual(["TC-1", "TC-2", "TC-3"]);
  });

  it("puts the order back and says why when the save fails", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createErrorResult(409, "SUITE_ARCHIVED"));
    renderDetail();
    await screen.findByRole("list", { name: cases.listLabel });

    await openCaseMenu(user, "TC-1");
    await user.click(await screen.findByRole("menuitem", { name: cases.moveDown }));

    expect(await screen.findByText(englishSuites.errors.archived)).toBeInTheDocument();
    expect(readCodes()).toEqual(["TC-1", "TC-2", "TC-3"]);
  });

  it("shows a read-only list to a viewer", async () => {
    renderDetail(VIEWER_PROJECT);

    expect(await screen.findByRole("list", { name: cases.listLabel })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Reorder TC-1" })).toBeNull();
    expect(screen.queryByRole("button", { name: cases.addCases })).toBeNull();
    expect(screen.queryByRole("button", { name: detail.actionsLabel })).toBeNull();
    expect(screen.queryByRole("link", { name: detail.startManualRun })).toBeNull();
    expect(screen.getByText('/tessio:run-suite "Checkout regression"')).toBeInTheDocument();
  });

  it("locks an archived suite", async () => {
    respondWithRoutes(apiGet, {
      [SUITE_PATH]: createSuccessResult(buildSuiteDetail({ archivedAt: "2026-10-30T09:00:00Z" })),
    });
    renderDetail();

    expect(await screen.findByText(detail.archivedTitle)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Reorder TC-1" })).toBeNull();
    expect(screen.queryByRole("button", { name: cases.addByFilter })).toBeNull();
    expect(screen.queryByRole("link", { name: detail.startManualRun })).toBeNull();
    expect(screen.queryByText(command.title)).toBeNull();
  });

  it("links the running run and hides the manual start", async () => {
    respondWithRoutes(apiGet, {
      [SUITE_PATH]: createSuccessResult(
        buildSuiteDetail({
          runningRun: {
            id: RUN_ID,
            status: "running",
            startedAt: "2026-11-01T09:00:00Z",
            finishedAt: null,
          },
        }),
      ),
    });
    renderDetail();

    expect(await screen.findByText(detail.runningTitle)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.openRun })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs/${RUN_ID}`,
    );
    expect(screen.queryByRole("link", { name: detail.startManualRun })).toBeNull();
  });

  it("shows the not-found state for an unknown or invalid suite", async () => {
    respondWithRoutes(apiGet, { [SUITE_PATH]: createErrorResult(404, "NOT_FOUND") });
    const { unmount } = renderDetail();

    expect(await screen.findByText(detail.notFoundTitle)).toBeInTheDocument();
    unmount();

    renderDetail(QC_PROJECT, "not-a-suite");
    expect(screen.getByText(detail.notFoundTitle)).toBeInTheDocument();
    expect(apiGet).toHaveBeenCalledTimes(1);
  });

  it("renames the suite and sends only the changed field", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [SUITE_PATH]: createSuccessResult(buildSuiteDetail({ name: "Checkout" })),
    });
    renderDetail();
    await screen.findByRole("heading", { name: "Checkout regression" });

    await user.click(screen.getByRole("button", { name: detail.actionsLabel }));
    await user.click(await screen.findByRole("menuitem", { name: detail.edit }));
    const dialog = await screen.findByRole("dialog");
    const nameInput = within(dialog).getByRole("textbox", { name: /^Name/ });
    await user.clear(nameInput);
    await user.type(nameInput, "Checkout");
    await user.click(within(dialog).getByRole("button", { name: form.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(SUITE_PATH, {
        params: { path: { project_key: "SHOP", suite_id: SUITE_ID } },
        body: { name: "Checkout" },
      });
    });
    expect(await screen.findByText(toasts.updated)).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Checkout" })).toBeInTheDocument();
  });

  it("archives the suite after asking", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPost, {
      [ARCHIVE_PATH]: createSuccessResult(buildSuiteDetail({ archivedAt: "2026-11-02T09:00:00Z" })),
    });
    renderDetail();
    await screen.findByRole("heading", { name: "Checkout regression" });

    await user.click(screen.getByRole("button", { name: detail.actionsLabel }));
    await user.click(await screen.findByRole("menuitem", { name: detail.archive }));
    const dialog = await screen.findByRole("dialog", { name: archive.title });
    await user.click(within(dialog).getByRole("button", { name: archive.confirm }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(ARCHIVE_PATH, {
        params: { path: { project_key: "SHOP", suite_id: SUITE_ID } },
      });
    });
    expect(await screen.findByText(archive.done)).toBeInTheDocument();
    expect(await screen.findByText(detail.archivedTitle)).toBeInTheDocument();
  });
});
