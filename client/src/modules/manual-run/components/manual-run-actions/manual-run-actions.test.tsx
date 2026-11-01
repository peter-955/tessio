import { VIEWER_CAPABILITIES } from "@/components/project-context/test/utils/project-fixture.util";
import englishManualRun from "@/lib/i18n/locales/en/manualRun.json";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet, apiPost } from "../../test/mocks/api-client.mock";
import { routerPush } from "../../test/mocks/next-navigation.mock";
import {
  createCreatedResult,
  createErrorResult,
  createSuccessResult,
  respondWithRoutes,
} from "../../test/utils/api-result.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import {
  CURRENT_USER_ID,
  NEW_RUN_ID,
  OTHER_USER_ID,
  PRODUCTION_ID,
  RUN_ID,
  buildCreatedRun,
  buildEnvironment,
  buildRunProject,
} from "../../test/utils/run.fixture";
import { chooseSelectOption } from "../../test/utils/select-option.util";
import { stubDocumentFonts } from "../../test/utils/stub-document-fonts.util";
import { stubScrollIntoView } from "../../test/utils/stub-scroll-into-view.util";
import type { ManualRunActionsRun } from "../../typing/types/manual-run-actions-run.type";
import { NewManualRunButtonLink } from "../new-manual-run-button-link/new-manual-run-button-link";
import { ManualRunActions } from "./manual-run-actions";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", async () => {
  return (await import("../../test/mocks/current-user.mock")).currentUserMock;
});

vi.mock("next/navigation", async () => {
  return (await import("../../test/mocks/next-navigation.mock")).nextNavigationMock;
});

const ENVIRONMENTS_PATH = "/api/projects/{project_key}/environments";
const RERUN_PATH = "/api/projects/{project_key}/runs/{run_id}/rerun-failed";

const { actions, errors, rerun } = englishManualRun;

const FINISHED_MANUAL_RUN: ManualRunActionsRun = {
  id: RUN_ID,
  executor: "manual",
  status: "failed",
  startedBy: CURRENT_USER_ID,
  failedCount: 2,
  blockedCount: 1,
};

const renderActions = (
  run: ManualRunActionsRun,
  project = buildRunProject(),
): ReturnType<typeof renderWithProject> => {
  return renderWithProject(<ManualRunActions run={run} />, project);
};

const expectNoActions = (): void => {
  expect(screen.queryByRole("button")).not.toBeInTheDocument();
  expect(screen.queryByRole("link")).not.toBeInTheDocument();
};

const rerunLabel = (count: number): string => {
  return rerun.action.replace("{{count}}", String(count));
};

describe("ManualRunActions", () => {
  beforeAll(() => {
    stubScrollIntoView();
    stubDocumentFonts();
  });

  beforeEach(() => {
    respondWithRoutes(apiGet, {
      [ENVIRONMENTS_PATH]: createSuccessResult([
        buildEnvironment(),
        buildEnvironment({ id: PRODUCTION_ID, name: "Production" }),
      ]),
    });
    respondWithRoutes(apiPost, { [RERUN_PATH]: createCreatedResult(buildCreatedRun()) });
  });

  it("shows the plugin command for a finished Claude run", async () => {
    const user = userEvent.setup();
    renderActions({ ...FINISHED_MANUAL_RUN, executor: "claude" });

    await user.click(screen.getByRole("button", { name: rerunLabel(3) }));
    const dialog = await screen.findByRole("dialog", { name: rerun.claudeTitle });

    expect(within(dialog).getByText(`/tessio:rerun-failed ${RUN_ID}`)).toBeInTheDocument();
    expect(within(dialog).getByText(rerun.claudeNote)).toBeInTheDocument();
    expect(await axe(dialog)).toHaveNoViolations();

    await user.click(within(dialog).getByRole("button", { name: rerun.manualInstead }));
    expect(await screen.findByRole("dialog", { name: rerun.manualTitle })).toBeInTheDocument();
  });

  it("hides the manual switch on a Claude run without run.record_manual", async () => {
    const user = userEvent.setup();
    renderActions(
      { ...FINISHED_MANUAL_RUN, executor: "claude" },
      buildRunProject({ capabilities: [...VIEWER_CAPABILITIES, "run.start"] }),
    );

    await user.click(screen.getByRole("button", { name: rerunLabel(3) }));
    const dialog = await screen.findByRole("dialog", { name: rerun.claudeTitle });

    expect(
      within(dialog).queryByRole("button", { name: rerun.manualInstead }),
    ).not.toBeInTheDocument();
  });

  it("creates a manual child run and opens its record page", async () => {
    const user = userEvent.setup();
    renderActions(FINISHED_MANUAL_RUN);

    await user.click(screen.getByRole("button", { name: rerunLabel(3) }));
    const dialog = await screen.findByRole("dialog", { name: rerun.manualTitle });
    expect(
      within(dialog).getByText(rerun.manualDescription_other.replace("{{count}}", "3")),
    ).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: rerun.confirm }));

    await waitFor(() => {
      expect(routerPush).toHaveBeenCalledWith(`/projects/SHOP/runs/${NEW_RUN_ID}/record`);
    });
    expect(apiPost).toHaveBeenCalledWith(
      RERUN_PATH,
      expect.objectContaining({
        params: { path: { project_key: "SHOP", run_id: RUN_ID } },
        body: { environmentId: null },
      }),
    );
  });

  it("sends the picked environment for the re-run", async () => {
    const user = userEvent.setup();
    renderActions(FINISHED_MANUAL_RUN);

    await user.click(screen.getByRole("button", { name: rerunLabel(3) }));
    const dialog = await screen.findByRole("dialog", { name: rerun.manualTitle });
    await chooseSelectOption(user, /^Environment/, "Production");
    await user.click(within(dialog).getByRole("button", { name: rerun.confirm }));

    await waitFor(() => {
      expect(apiPost).toHaveBeenCalledWith(
        RERUN_PATH,
        expect.objectContaining({ body: { environmentId: PRODUCTION_ID } }),
      );
    });
  });

  it("shows NO_FAILED_CASES_TO_RERUN inline", async () => {
    respondWithRoutes(apiPost, {
      [RERUN_PATH]: createErrorResult(409, "NO_FAILED_CASES_TO_RERUN"),
    });
    const user = userEvent.setup();
    renderActions(FINISHED_MANUAL_RUN);

    await user.click(screen.getByRole("button", { name: rerunLabel(3) }));
    const dialog = await screen.findByRole("dialog", { name: rerun.manualTitle });
    await user.click(within(dialog).getByRole("button", { name: rerun.confirm }));

    expect(await within(dialog).findByText(errors.noFailedCases)).toBeInTheDocument();
    expect(routerPush).not.toHaveBeenCalled();
  });

  it("renders nothing for a running Claude run", () => {
    renderActions({
      ...FINISHED_MANUAL_RUN,
      executor: "claude",
      status: "running",
    });

    expectNoActions();
  });

  it("renders nothing for a finished run without failures", () => {
    renderActions({
      ...FINISHED_MANUAL_RUN,
      status: "passed",
      failedCount: 0,
      blockedCount: 0,
    });

    expectNoActions();
  });

  it("renders nothing for a viewer", () => {
    renderActions(FINISHED_MANUAL_RUN, buildRunProject({ capabilities: VIEWER_CAPABILITIES }));

    expectNoActions();
  });

  it("renders nothing on an archived project", () => {
    renderActions(FINISHED_MANUAL_RUN, buildRunProject({ isArchived: true }));

    expectNoActions();
  });

  it("offers Continue recording to the starter of a running manual run", () => {
    renderActions({ ...FINISHED_MANUAL_RUN, status: "running" });

    expect(screen.getByRole("link", { name: actions.continue })).toHaveAttribute(
      "href",
      `/projects/SHOP/runs/${RUN_ID}/record`,
    );
    expect(screen.queryByRole("button", { name: rerunLabel(3) })).not.toBeInTheDocument();
  });

  it("hides Continue recording from another QC but shows it to a run.finish_any role", () => {
    const run = { ...FINISHED_MANUAL_RUN, status: "running" as const, startedBy: OTHER_USER_ID };
    const { unmount } = renderActions(run);

    expect(screen.queryByRole("link", { name: actions.continue })).not.toBeInTheDocument();
    unmount();

    renderActions(
      run,
      buildRunProject({ capabilities: [...buildRunProject().capabilities, "run.finish_any"] }),
    );
    expect(screen.getByRole("link", { name: actions.continue })).toBeInTheDocument();
  });
});

describe("NewManualRunButtonLink", () => {
  it("links to the new run page with the story", () => {
    renderWithProject(<NewManualRunButtonLink storyKey="SHOP-1" />, buildRunProject());

    expect(screen.getByRole("link", { name: actions.newRun })).toHaveAttribute(
      "href",
      "/projects/SHOP/runs/new?story=SHOP-1",
    );
  });

  it("is hidden from a viewer", () => {
    renderWithProject(
      <NewManualRunButtonLink />,
      buildRunProject({ capabilities: VIEWER_CAPABILITIES }),
    );

    expectNoActions();
  });
});
