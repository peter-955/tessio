import englishSharedSteps from "@/lib/i18n/locales/en/sharedSteps.json";
import {
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "@/modules/auth/test/utils/api-result.util";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { SharedStepDetailPage } from "./shared-step-detail";
import { apiGet, apiPatch } from "./test/mocks/api-client.mock";
import { interpolate } from "./test/utils/interpolate.util";
import { renderWithProject } from "./test/utils/render-with-project.util";
import { QC_PROJECT, VIEWER_PROJECT } from "./test/utils/shared-step-project.util";
import { buildSharedStep, buildSharedStepUsage } from "./test/utils/shared-step.fixture";
import { stubDocumentFonts } from "./test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "./test/utils/stub-scroll-into-view.util";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("./test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("./test/mocks/next-navigation.mock")).nextNavigationMock;
});

const SHARED_STEP_PATH = "/api/projects/{project_key}/shared-steps/{key}";
const USAGE_PATH = "/api/projects/{project_key}/shared-steps/{key}/usage";
const TEST_DATA_PATH = "/api/projects/{project_key}/test-data";

const { detail, usage, form, toasts, reference } = englishSharedSteps;

const SHARED_STEP = buildSharedStep();

describe("SharedStepDetailPage", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    apiGet.mockReset();
    apiPatch.mockReset();
    respondWithRoutes(apiGet, {
      [SHARED_STEP_PATH]: createSuccessResult(SHARED_STEP),
      [USAGE_PATH]: createSuccessResult([
        buildSharedStepUsage(),
        buildSharedStepUsage({
          testCaseId: "e3000000-0000-4000-8000-000000000002",
          code: "TC-9",
          title: "Cancel an order",
          status: "draft",
        }),
      ]),
      [TEST_DATA_PATH]: createSuccessResult([]),
    });
  });

  it("shows the steps and the cases that use the shared step", async () => {
    const { container } = renderWithProject(
      <SharedStepDetailPage sharedStepKey="Login_As_Admin" />,
      QC_PROJECT,
    );

    expect(await screen.findByRole("heading", { name: "Log in as admin" })).toBeInTheDocument();
    const steps = screen.getByRole("list", {
      name: interpolate(reference.stepsOf, { title: "Log in as admin" }),
    });
    expect(within(steps).getByText("Open the sign-in page")).toBeInTheDocument();
    expect(within(steps).getByText("The dashboard shows")).toBeInTheDocument();
    expect(
      screen.getByText(interpolate(detail.dataKeys, { keys: "admin_email" })),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: interpolate(usage.count_other, { count: 3 }) }),
    ).toBeInTheDocument();
    const usageTable = await screen.findByRole("table", { name: usage.tableLabel });
    expect(within(usageTable).getByRole("link", { name: "TC-4" })).toHaveAttribute(
      "href",
      "/projects/SHOP/test-cases/TC-4",
    );
    expect(within(usageTable).getByText("Cancel an order")).toBeInTheDocument();
    expect(apiGet).toHaveBeenCalledWith(
      SHARED_STEP_PATH,
      expect.objectContaining({
        params: { path: { project_key: "SHOP", key: "login_as_admin" } },
      }),
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("archives the shared step without a new version", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [SHARED_STEP_PATH]: createSuccessResult(
        buildSharedStep({ isArchived: true, archivedAt: "2026-11-01T10:00:00Z" }),
      ),
    });
    renderWithProject(<SharedStepDetailPage sharedStepKey="login_as_admin" />, QC_PROJECT);

    await user.click(await screen.findByRole("button", { name: detail.archive }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(SHARED_STEP_PATH, {
        params: { path: { project_key: "SHOP", key: "login_as_admin" } },
        body: { baseVersionNumber: 2, archived: true },
      });
    });
    expect(
      await screen.findByText(interpolate(toasts.archived, { title: "Log in as admin" })),
    ).toBeInTheDocument();
    expect(await screen.findByText(detail.archivedNotice)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: detail.restore })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: detail.edit })).not.toBeInTheDocument();
  });

  it("saves new steps from the edit dialog", async () => {
    const user = userEvent.setup();
    respondWithRoutes(apiPatch, {
      [SHARED_STEP_PATH]: createSuccessResult(SHARED_STEP),
    });
    renderWithProject(<SharedStepDetailPage sharedStepKey="login_as_admin" />, QC_PROJECT);

    await user.click(await screen.findByRole("button", { name: detail.edit }));
    const dialog = await screen.findByRole("dialog", { name: form.editTitle });
    expect(
      within(dialog).queryByRole("textbox", { name: new RegExp(`^${form.key}`) }),
    ).not.toBeInTheDocument();
    const [firstAction] = within(dialog).getAllByRole("textbox", {
      name: new RegExp(`^${form.action}`),
    });
    if (firstAction === undefined) {
      throw new Error("The dialog shows the steps.");
    }
    await user.clear(firstAction);
    await user.type(firstAction, "Open the admin sign-in page");
    await user.click(within(dialog).getByRole("button", { name: form.save }));

    await waitFor(() => {
      expect(apiPatch).toHaveBeenCalledWith(SHARED_STEP_PATH, {
        params: { path: { project_key: "SHOP", key: "login_as_admin" } },
        body: {
          baseVersionNumber: 2,
          steps: [
            { action: "Open the admin sign-in page", expected: null },
            { action: "Sign in as {{data.admin_email}}", expected: "The dashboard shows" },
          ],
        },
      });
    });
  });

  it("hides the actions for a viewer", async () => {
    renderWithProject(<SharedStepDetailPage sharedStepKey="login_as_admin" />, VIEWER_PROJECT);

    expect(await screen.findByRole("heading", { name: "Log in as admin" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: detail.edit })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: detail.archive })).not.toBeInTheDocument();
  });

  it("shows not found for an unknown or invalid key", async () => {
    respondWithRoutes(apiGet, { [SHARED_STEP_PATH]: createErrorResult(404, "NOT_FOUND") });
    renderWithProject(<SharedStepDetailPage sharedStepKey="missing_step" />, QC_PROJECT);

    expect(await screen.findByText(detail.notFoundTitle)).toBeInTheDocument();
  });

  it("does not ask the server for a key that can't exist", () => {
    renderWithProject(<SharedStepDetailPage sharedStepKey="1-bad" />, QC_PROJECT);

    expect(screen.getByText(detail.notFoundTitle)).toBeInTheDocument();
    expect(apiGet).not.toHaveBeenCalledWith(SHARED_STEP_PATH, expect.anything());
  });
});
