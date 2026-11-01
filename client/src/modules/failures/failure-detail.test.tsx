import type { ProjectCapability } from "@/components/project-context/typing/types/project.type";
import englishFailures from "@/lib/i18n/locales/en/failures.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { FailureDetailPage } from "./failure-detail";
import { apiGet, apiPut } from "./test/mocks/api-client.mock";
import { setNavigation } from "./test/mocks/next-navigation.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import {
  ASSIGNEE_ID,
  CURRENT_USER_ID,
  DEACTIVATED_USER_ID,
  FAILURE_ID,
  MEMBERS,
  buildFailure,
  buildFailureDetail,
  buildFailureRun,
} from "./test/utils/failure-fixture.util";
import {
  DEV_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
  buildProject,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { FailureDetail } from "./typing/types/failure.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface PutRequest {
  body: Record<string, unknown>;
}

const FAILURE_PATH = "/api/projects/{project_key}/failures/{failure_id}";
const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";
const FILE_PATH = "/api/projects/{project_key}/files/{file_id}";
const MEMBERS_PATH = "/api/projects/{project_key}/members";
const STATUS_PATH = "/api/projects/{project_key}/failures/{failure_id}/status";
const ASSIGNEE_PATH = "/api/projects/{project_key}/failures/{failure_id}/assignee";
const SIGNED_URL = "https://files.example.test/signed/shot.png";

const { actions, assign, detail, history, screenshot, step, timeline } = englishFailures;

interface Routes {
  failure?: ApiResult | (() => ApiResult);
  run?: ApiResult;
  file?: ApiResult;
}

const respond = ({
  failure = createSuccessResult(buildFailureDetail()),
  run = createSuccessResult(buildFailureRun()),
  file = createSuccessResult({ url: SIGNED_URL, expiresAt: "2026-10-21T10:35:00Z" }),
}: Routes = {}): void => {
  respondWithRoutes(apiGet, {
    [FAILURE_PATH]: failure,
    [RUN_PATH]: run,
    [FILE_PATH]: file,
    [MEMBERS_PATH]: createSuccessResult(MEMBERS),
  });
};

const renderPage = (
  capabilities: ProjectCapability[] = VIEWER_CAPABILITIES,
  failureId = FAILURE_ID,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(
    <FailureDetailPage failureId={failureId} />,
    buildProject({ capabilities }),
  );
};

const findTitle = (): Promise<HTMLElement> => {
  return screen.findByRole("heading", { name: "TC-1 · Pay with a valid card" });
};

const readPutBodies = (path: string): Record<string, unknown>[] => {
  return apiPut.mock.calls
    .filter(([calledPath]) => {
      return calledPath === path;
    })
    .map(([, options]) => {
      return (options as PutRequest).body;
    });
};

const openAssignModal = async (user: UserEvent, label: string): Promise<HTMLElement> => {
  await findTitle();
  await user.click(screen.getByRole("button", { name: label }));

  return screen.findByRole("dialog", { name: assign.title });
};

const withFailure = (overrides: Partial<FailureDetail>): Routes => {
  return { failure: createSuccessResult(buildFailureDetail(overrides)) };
};

describe("FailureDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPut.mockReset();
    setNavigation(`/projects/SHOP/failures/${FAILURE_ID}`);
    respond();
  });

  it("shows the failed step, the screenshot, the timeline and the history", async () => {
    const { container } = renderPage();

    await findTitle();
    expect(screen.getByRole("link", { name: "SHOP-1 · Pay by card" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-1",
    );
    expect(screen.getByRole("link", { name: "TC-1" })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/TC-1",
    );
    expect(screen.getByText(step.title)).toBeInTheDocument();
    expect(screen.getByText("Step 2")).toBeInTheDocument();
    expect(await screen.findByText("Click Pay with a valid card")).toBeInTheDocument();
    expect(screen.getByText("The order is confirmed")).toBeInTheDocument();
    expect(screen.getAllByText("The pay button stayed disabled").length).toBeGreaterThan(0);
    expect(screen.getByText("TimeoutError: button not enabled")).toBeInTheDocument();
    expect(await screen.findByRole("img", { name: "Screenshot of step 2" })).toHaveAttribute(
      "src",
      SIGNED_URL,
    );
    expect(screen.getByText(timeline.opened)).toBeInTheDocument();
    expect(screen.getByText("Assigned to Dev Dana")).toBeInTheDocument();
    expect(screen.getByText(timeline.automatic)).toBeInTheDocument();
    expect(screen.getByText("by Quinn Qc")).toBeInTheDocument();
    const historyCard = within(
      screen.getByRole("heading", { name: history.title }).parentElement as HTMLElement,
    );
    expect(historyCard.getByText(englishFailures.result.failed)).toBeInTheDocument();
    expect(historyCard.getByText(englishFailures.executor.claude)).toBeInTheDocument();
    expect(historyCard.getByText("Quinn Qc")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("says the screenshot is still uploading while the run is running", async () => {
    respond({
      run: createSuccessResult(buildFailureRun("pending", { status: "running", finishedAt: null })),
    });
    renderPage();

    expect(await screen.findByText(screenshot.uploading)).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("says a pending screenshot is missing once the run has ended", async () => {
    respond({ run: createSuccessResult(buildFailureRun("pending", { status: "aborted" })) });
    renderPage();

    expect(await screen.findByText(screenshot.missing)).toBeInTheDocument();
    expect(screen.queryByText(screenshot.uploading)).not.toBeInTheDocument();
  });

  it("says the screenshot is missing or unavailable", async () => {
    respond({ run: createSuccessResult(buildFailureRun("missing")) });
    const { unmount } = renderPage();

    expect(await screen.findByText(screenshot.missing)).toBeInTheDocument();
    unmount();

    respond({ file: createErrorResult(404, "NOT_FOUND") });
    renderPage();

    expect(await screen.findByText(screenshot.unavailable)).toBeInTheDocument();
  });

  it("still shows the failure's own step fields when the run cannot load", async () => {
    respond({ run: createErrorResult(500, "CONFLICT") });
    renderPage();

    await findTitle();
    expect(await screen.findByRole("img", { name: "Screenshot of step 2" })).toBeInTheDocument();
    expect(screen.queryByText(step.action)).not.toBeInTheDocument();
    expect(screen.getByText("TimeoutError: button not enabled")).toBeInTheDocument();
  });

  it("reports when no step failed", async () => {
    respond(withFailure({ failedStep: null }));
    renderPage();

    expect(await screen.findByText(step.none)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: step.openRun })).toHaveAttribute(
      "href",
      "/projects/SHOP/runs/b1000000-0000-4000-8000-000000000001",
    );
  });

  it("lets a developer mark the failure fixed", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createSuccessResult(buildFailure({ status: "fixed" })));
    renderPage(DEV_CAPABILITIES);

    await findTitle();
    expect(screen.queryByRole("button", { name: actions.verify })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.reopen })).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: actions.markFixed }));

    await waitFor(() => {
      expect(readPutBodies(STATUS_PATH)).toEqual([{ status: "fixed" }]);
    });
    expect(await screen.findByText("TC-1 is now Fixed.")).toBeInTheDocument();
    await waitFor(() => {
      expect(
        apiGet.mock.calls.filter(([path]) => {
          return path === FAILURE_PATH;
        }).length,
      ).toBeGreaterThan(1);
    });
  });

  it("lets a tester verify or reopen a fixed failure", async () => {
    respond(withFailure({ status: "fixed" }));
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createSuccessResult(buildFailure({ status: "reopened" })));
    renderPage(QC_CAPABILITIES);

    await findTitle();
    expect(screen.getByRole("button", { name: actions.verify })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.markFixed })).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: actions.reopen }));

    await waitFor(() => {
      expect(readPutBodies(STATUS_PATH)).toEqual([{ status: "reopened" }]);
    });
  });

  it("shows no actions to a viewer", async () => {
    renderPage(VIEWER_CAPABILITIES);

    await findTitle();
    for (const label of [actions.markFixed, actions.verify, actions.reopen, actions.assign]) {
      expect(screen.queryByRole("button", { name: label })).not.toBeInTheDocument();
    }
  });

  it("hides Assign on a verified failure", async () => {
    respond(withFailure({ status: "verified", isActive: false }));
    renderPage(QC_CAPABILITIES);

    await findTitle();
    expect(screen.queryByRole("button", { name: actions.assign })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.verify })).not.toBeInTheDocument();
  });

  it("assigns an active member from the picker", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(
      createSuccessResult(
        buildFailure({
          assigneeId: ASSIGNEE_ID,
          assigneeName: "Dev Dana",
          assigneeStatus: "active",
        }),
      ),
    );
    renderPage(QC_CAPABILITIES);

    const dialog = await openAssignModal(user, actions.assign);
    const save = within(dialog).getByRole("button", { name: assign.submit });
    await waitFor(() => {
      expect(save).toBeDisabled();
    });
    const option = await openSelectOption(user, /^Assignee/, "Dev Dana · Dev");
    const listbox = option.closest("[role='listbox']") as HTMLElement;
    expect(
      within(listbox)
        .getAllByRole("option", { hidden: true })
        .map((element) => element.textContent),
    ).toEqual([assign.unassigned, "Dev Dana · Dev", "Quinn Qc · QC"]);
    await user.click(option);
    await user.click(save);

    await waitFor(() => {
      expect(readPutBodies(ASSIGNEE_PATH)).toEqual([{ assigneeId: ASSIGNEE_ID }]);
    });
    expect(await screen.findByText("TC-1 assigned to Dev Dana.")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: assign.title })).not.toBeInTheDocument();
    });
  });

  it("unassigns the failure", async () => {
    respond(
      withFailure({ assigneeId: ASSIGNEE_ID, assigneeName: "Dev Dana", assigneeStatus: "active" }),
    );
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createSuccessResult(buildFailure()));
    renderPage(QC_CAPABILITIES);

    const dialog = await openAssignModal(user, actions.reassign);
    await user.click(await openSelectOption(user, /^Assignee/, assign.unassigned));
    await user.click(within(dialog).getByRole("button", { name: assign.submit }));

    await waitFor(() => {
      expect(readPutBodies(ASSIGNEE_PATH)).toEqual([{ assigneeId: null }]);
    });
    expect(await screen.findByText("TC-1 is now unassigned.")).toBeInTheDocument();
  });

  it("shows an inline error when the assignee is no longer active", async () => {
    const user = userEvent.setup();
    apiPut.mockResolvedValue(createErrorResult(409, "ASSIGNEE_NOT_ACTIVE_MEMBER"));
    renderPage(QC_CAPABILITIES);

    const dialog = await openAssignModal(user, actions.assign);
    await user.click(await openSelectOption(user, /^Assignee/, "Quinn Qc · QC"));
    await user.click(within(dialog).getByRole("button", { name: assign.submit }));

    expect(
      await within(dialog).findByText(englishFailures.errors.assigneeNotActive),
    ).toBeInTheDocument();
    expect(readPutBodies(ASSIGNEE_PATH)).toEqual([{ assigneeId: CURRENT_USER_ID }]);
  });

  it("warns about a deactivated assignee", async () => {
    respond(
      withFailure({
        assigneeId: DEACTIVATED_USER_ID,
        assigneeName: "Ann Old",
        assigneeStatus: "deactivated",
      }),
    );
    renderPage(QC_CAPABILITIES);

    expect(await screen.findByText(englishFailures.assignee.deactivatedHint)).toBeInTheDocument();
    expect(screen.getByText(englishFailures.assignee.deactivated)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: actions.reassign })).toBeInTheDocument();
  });

  it("shows the not-found state for a missing or invalid failure", async () => {
    respond({ failure: createErrorResult(404, "NOT_FOUND") });
    const { container, unmount } = renderPage();

    expect(await screen.findByText(detail.notFoundTitle)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/failures",
    );
    expect(await axe(container)).toHaveNoViolations();
    unmount();

    renderPage(VIEWER_CAPABILITIES, "not-a-uuid");

    expect(screen.getByText(detail.notFoundTitle)).toBeInTheDocument();
    expect(
      apiGet.mock.calls.filter(([path]) => {
        return path === FAILURE_PATH;
      }),
    ).toHaveLength(1);
  });

  it("offers a retry after a load error", async () => {
    const user = userEvent.setup();
    let isFailing = true;
    respond({
      failure: () => {
        return isFailing
          ? createErrorResult(500, "CONFLICT")
          : createSuccessResult(buildFailureDetail());
      },
    });
    renderPage();

    expect(await screen.findByText(detail.loadError)).toBeInTheDocument();
    isFailing = false;
    await user.click(screen.getByRole("button", { name: englishFailures.retry }));

    expect(await findTitle()).toBeInTheDocument();
  });
});
