import type { ProjectCapability } from "@/components/project-context/typing/types/project.type";
import englishPlans from "@/lib/i18n/locales/en/plans.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent, { type UserEvent } from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { PlanDetailPage } from "./plan-detail";
import { apiGet, apiPatch, apiPost, apiPut } from "./test/mocks/api-client.mock";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
  type ApiResult,
} from "./test/utils/api-result.util";
import {
  FAILURE_ID,
  OTHER_STORY_ID,
  OTHER_SUITE_ID,
  PLAN_ID,
  PLAN_STORIES,
  PLAN_SUITES,
  RUN_ID,
  STORY_ID,
  SUITE_ID,
  buildPassingPlanDetail,
  buildPlanDetail,
} from "./test/utils/plan-fixture.util";
import {
  PM_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
  buildProject,
} from "./test/utils/project-fixture.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { openSelectOption } from "./test/utils/select-option.util";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";
import type { PlanDetail } from "./typing/types/plan.type";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

interface BodyRequest {
  body: Record<string, unknown>;
}

const PLAN_PATH = "/api/projects/{project_key}/plans/{plan_id}";
const ITEMS_PATH = "/api/projects/{project_key}/plans/{plan_id}/items";
const SIGN_OFF_PATH = "/api/projects/{project_key}/plans/{plan_id}/sign-off";
const CLOSE_PATH = "/api/projects/{project_key}/plans/{plan_id}/close";
const SUITES_PATH = "/api/projects/{project_key}/suites";
const STORIES_PATH = "/api/projects/{project_key}/stories";
const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";

const { actions, blockers, cases, close, detail, form, items, progress, signOff, toasts } =
  englishPlans;

const respond = (plan: ApiResult | (() => ApiResult) = createSuccessResult(buildPlanDetail())) => {
  respondWithRoutes(apiGet, {
    [PLAN_PATH]: plan,
    [SUITES_PATH]: createSuccessResult(PLAN_SUITES),
    [STORIES_PATH]: createSuccessResult(PLAN_STORIES),
    [ENVIRONMENTS_PATH]: createSuccessResult([]),
  });
};

const respondWithPlan = (overrides: Partial<PlanDetail>): void => {
  respond(createSuccessResult(buildPlanDetail(overrides)));
};

const renderPage = (
  capabilities: ProjectCapability[] = VIEWER_CAPABILITIES,
  planId = PLAN_ID,
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<PlanDetailPage planId={planId} />, buildProject({ capabilities }));
};

const findTitle = (): Promise<HTMLElement> => {
  return screen.findByRole("heading", { name: "Release 4.2", level: 1 });
};

const openDialog = async (user: UserEvent, buttonName: string, title: string) => {
  await findTitle();
  await user.click(screen.getByRole("button", { name: buttonName }));

  return screen.findByRole("dialog", { name: title });
};

describe("PlanDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiPut.mockReset();
    apiPatch.mockReset();
  });

  it("shows the plan's progress, cases, blockers and items", async () => {
    respond();
    const { container } = renderPage();

    await findTitle();
    expect(screen.getByText("33% passed")).toBeInTheDocument();
    expect(screen.getByText("1 of 3 cases passed")).toBeInTheDocument();
    expect(screen.getByRole("progressbar", { name: "Failed: 1" })).toBeInTheDocument();
    expect(screen.getByText("Staging")).toBeInTheDocument();
    expect(screen.getByText(/Created by Quinn Qc/)).toBeInTheDocument();

    const caseTable = screen.getByRole("region", { name: cases.tableLabel });
    const failedRow = within(caseTable).getByRole("row", { name: /TC-2/ });
    expect(within(failedRow).getByRole("link", { name: /Failed/ })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs/${RUN_ID}`,
    );
    expect(within(failedRow).getByRole("link", { name: /Open/ })).toHaveAttribute(
      "href",
      `/projects/SHOP/failures/${FAILURE_ID}`,
    );
    const draftRow = within(caseTable).getByRole("row", { name: /TC-3/ });
    expect(within(draftRow).getByText("Not run")).toBeInTheDocument();
    expect(within(draftRow).getByText(cases.caseStatus.draft)).toBeInTheDocument();
    expect(within(draftRow).getByText(cases.needsReview)).toBeInTheDocument();

    expect(
      screen.getAllByRole("link", { name: "TC-2 · Refuse an expired card" }).map((link) => {
        return link.getAttribute("href");
      }),
    ).toEqual(["/projects/SHOP/test-cases/TC-2", `/projects/SHOP/failures/${FAILURE_ID}`]);
    expect(screen.getByText("Which card brands are accepted?")).toBeInTheDocument();
    expect(screen.getByText("BA role")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Checkout regression" })).toHaveAttribute(
      "href",
      `/projects/SHOP/suites/${SUITE_ID}`,
    );
    expect(screen.getByRole("link", { name: "SHOP-12 · Checkout" })).toHaveAttribute(
      "href",
      "/projects/SHOP/stories/SHOP-12",
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("filters the cases by status", async () => {
    const user = userEvent.setup();
    respond();
    renderPage();

    await findTitle();
    await user.click(screen.getByRole("tab", { name: /Not run/ }));

    const caseTable = screen.getByRole("region", { name: cases.tableLabel });
    expect(within(caseTable).getByRole("row", { name: /TC-3/ })).toBeInTheDocument();
    expect(within(caseTable).queryByRole("row", { name: /TC-1/ })).not.toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /Blocked/ }));
    expect(screen.getByText(cases.noMatch)).toBeInTheDocument();
  });

  it("gives a viewer no write action", async () => {
    respond();
    renderPage();

    await findTitle();
    for (const name of [actions.edit, actions.chooseItems, actions.signOff, actions.close]) {
      expect(screen.queryByRole("button", { name })).not.toBeInTheDocument();
    }
  });

  it("lets a PM edit and close but not sign off", async () => {
    respond();
    renderPage(PM_CAPABILITIES);

    await findTitle();
    expect(screen.getByRole("button", { name: actions.edit })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: actions.close })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.signOff })).not.toBeInTheDocument();
  });

  it("refuses to sign off while failures on the plan's cases are active", async () => {
    const user = userEvent.setup();
    respond();
    renderPage(QC_CAPABILITIES);

    const dialog = await openDialog(
      user,
      actions.signOff,
      signOff.title.replace("{{name}}", "Release 4.2"),
    );

    expect(
      within(dialog).getByText(
        "Resolve the 1 active failure on this plan's cases before signing it off.",
      ),
    ).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: actions.signOff })).toBeDisabled();
    expect(apiPost).not.toHaveBeenCalled();
  });

  it("signs off a plan with no active failure and shows who signed it off", async () => {
    const user = userEvent.setup();
    const signedOffPlan = buildPassingPlanDetail({
      status: "signed_off",
      signedOffBy: "4f5a6b7c-8d9e-4f0a-9b2c-3d4e5f6a7b01",
      signedOffByName: "Quinn Qc",
      signedOffAt: "2026-11-02T12:00:00Z",
    });
    let currentPlan = buildPassingPlanDetail({
      progress: {
        ...buildPassingPlanDetail().progress,
        counts: { total: 2, passed: 1, failed: 0, blocked: 0, skipped: 0, notRun: 1 },
      },
    });
    respond(() => {
      return createSuccessResult(currentPlan);
    });
    apiPost.mockImplementation(() => {
      currentPlan = signedOffPlan;

      return Promise.resolve(createSuccessResult(signedOffPlan));
    });
    renderPage(QC_CAPABILITIES);

    const dialog = await openDialog(user, actions.signOff, "Sign off Release 4.2?");
    expect(within(dialog).getByText(signOff.message)).toBeInTheDocument();
    expect(within(dialog).getByText("1 case has not run yet.")).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: actions.signOff }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(SIGN_OFF_PATH, {
        params: { path: { project_key: "SHOP", plan_id: PLAN_ID } },
      });
    });
    expect(await screen.findByText(toasts.signedOff)).toBeInTheDocument();
    expect(await screen.findByText(/Signed off by Quinn Qc/)).toBeInTheDocument();
    expect(screen.getByText(progress.frozenSignedOff)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.signOff })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: actions.edit })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: actions.close })).toBeInTheDocument();
  });

  it("shows the server's refusal when failures appeared meanwhile", async () => {
    const user = userEvent.setup();
    respond(createSuccessResult(buildPassingPlanDetail()));
    apiPost.mockResolvedValue(createErrorResult(409, "PLAN_FAILURES_ACTIVE"));
    renderPage(QC_CAPABILITIES);

    const dialog = await openDialog(user, actions.signOff, "Sign off Release 4.2?");
    await user.click(within(dialog).getByRole("button", { name: actions.signOff }));

    expect(await screen.findByText(englishPlans.errors.failuresActive)).toBeInTheDocument();
  });

  it("closes a plan after confirmation", async () => {
    const user = userEvent.setup();
    respond();
    apiPost.mockResolvedValue(
      createSuccessResult(
        buildPlanDetail({
          status: "closed",
          closedBy: "4f5a6b7c-8d9e-4f0a-9b2c-3d4e5f6a7b01",
          closedByName: "Quinn Qc",
          closedAt: "2026-11-02T12:00:00Z",
        }),
      ),
    );
    renderPage(PM_CAPABILITIES);

    const dialog = await openDialog(user, actions.close, "Close Release 4.2?");
    expect(within(dialog).getByText(close.message)).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: actions.close }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(CLOSE_PATH, {
        params: { path: { project_key: "SHOP", plan_id: PLAN_ID } },
      });
    });
    expect(await screen.findByText(toasts.closed)).toBeInTheDocument();
  });

  it("edits the plan and sends only what changed", async () => {
    const user = userEvent.setup();
    respond();
    apiPatch.mockResolvedValue(createSuccessResult(buildPlanDetail({ name: "Release 4.3" })));
    renderPage(QC_CAPABILITIES);

    const dialog = await openDialog(user, actions.edit, form.editTitle);
    const nameInput = within(dialog).getByRole("textbox", { name: /Name/ });
    await user.clear(nameInput);
    await user.type(nameInput, "Release 4.3");
    await user.clear(within(dialog).getByRole("textbox", { name: form.description }));
    await user.click(within(dialog).getByRole("button", { name: form.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledTimes(1);
    });
    const [path, options] = apiPatch.mock.calls[0] ?? [];
    expect(path).toBe(PLAN_PATH);
    expect((options as BodyRequest).body).toEqual({ name: "Release 4.3", description: null });
    expect(await screen.findByText(toasts.updated)).toBeInTheDocument();
  });

  it("replaces the plan's suites and stories", async () => {
    const user = userEvent.setup();
    respond();
    apiPut.mockResolvedValue(createSuccessResult(buildPlanDetail()));
    renderPage(QC_CAPABILITIES);

    const dialog = await openDialog(user, actions.chooseItems, items.modalTitle);
    await user.click(await openSelectOption(user, /Regression suites/, "Search regression"));
    await user.click(await openSelectOption(user, /^Stories/, "SHOP-13 · Wish list"));
    await user.click(within(dialog).getByRole("button", { name: items.save }));

    await waitFor(() => {
      expect(apiPut).toHaveBeenCalledTimes(1);
    });
    const [path, options] = apiPut.mock.calls[0] ?? [];
    expect(path).toBe(ITEMS_PATH);
    expect((options as BodyRequest).body).toEqual({
      items: [
        { suiteId: SUITE_ID },
        { suiteId: OTHER_SUITE_ID },
        { storyId: STORY_ID },
        { storyId: OTHER_STORY_ID },
      ],
    });
    expect(await screen.findByText(toasts.itemsSaved)).toBeInTheDocument();
  });

  it("shows a plan that covers nothing yet", async () => {
    respondWithPlan({
      items: [],
      progress: {
        counts: { total: 0, passed: 0, failed: 0, blocked: 0, skipped: 0, notRun: 0 },
        cases: [],
        failures: [],
        gaps: [],
      },
    });
    renderPage();

    await findTitle();
    expect(screen.getByText(items.none)).toBeInTheDocument();
    expect(screen.getByText(cases.noCases)).toBeInTheDocument();
    expect(screen.getByText(blockers.noFailures)).toBeInTheDocument();
    expect(screen.getByText(blockers.noGaps)).toBeInTheDocument();
  });

  it("shows not found for another project's plan and for a malformed id", async () => {
    respond(createErrorResult(404, "NOT_FOUND"));
    const { unmount } = renderPage();

    expect(await screen.findByText(detail.notFoundTitle)).toBeInTheDocument();
    unmount();

    renderPage(VIEWER_CAPABILITIES, "not-a-uuid");
    expect(screen.getByText(detail.notFoundTitle)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: detail.back })).toHaveAttribute(
      "href",
      "/projects/SHOP/plans",
    );
  });
});
