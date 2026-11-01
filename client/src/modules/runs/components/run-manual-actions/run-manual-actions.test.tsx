import { VIEWER_CAPABILITIES } from "@/components/project-context/test/utils/project-fixture.util";
import type { ProjectCapability } from "@/components/project-context/typing/types/project.type";
import englishManualRun from "@/lib/i18n/locales/en/manualRun.json";
import { createSuccessResult, respondWithRoutes } from "@/modules/auth/test/utils/api-result.util";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import type { RunDetail } from "@/shared/typing/types/test-run.type";
import { tabTo } from "@/test/utils/tab-to.util";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { apiGet } from "../../test/mocks/api-client.mock";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { RUN_ID, createRunDetail } from "../../test/utils/run.fixture";
import { RunManualActions } from "./run-manual-actions";

const CURRENT_USER_ID = "b6000000-0000-4000-8000-000000000001";

vi.mock("@/lib/api/api-client", async () => {
  return (await import("../../test/mocks/api-client.mock")).apiClientMock;
});

vi.mock("next/navigation", async () => {
  return (await import("@/modules/auth/test/mocks/next-navigation.mock")).nextNavigationMock;
});

vi.mock("@/components/session-guard/hooks/use-current-user", () => {
  return {
    useCurrentUser: (): CurrentUser => {
      return {
        id: CURRENT_USER_ID,
        email: "alice@example.test",
        name: "Alice Tester",
        workspaceRole: "member",
        nextStep: "signed_in",
        language: "en",
        colorScheme: "auto",
        avatarFileId: null,
        avatarUrl: null,
        isTwoFactorSetUp: true,
      };
    },
  };
});

const RUN_PATH = "/api/projects/{project_key}/runs/{run_id}";

const QC_CAPABILITIES: ProjectCapability[] = [
  ...VIEWER_CAPABILITIES,
  "run.start",
  "run.record_manual",
];

const { actions, rerun } = englishManualRun;

const respondWithRun = (run: RunDetail): void => {
  respondWithRoutes(apiGet, { [RUN_PATH]: createSuccessResult(run) });
};

describe("RunManualActions", () => {
  beforeEach(() => {
    apiGet.mockReset();
  });

  it("offers Continue recording on the starter's running manual run", async () => {
    respondWithRun(
      createRunDetail({ executor: "manual", status: "running", startedBy: CURRENT_USER_ID }),
    );

    renderWithProject(<RunManualActions runId={RUN_ID} />, { capabilities: QC_CAPABILITIES });

    expect(await screen.findByRole("link", { name: actions.continue })).toHaveAttribute(
      "href",
      `/projects/APP/runs/${RUN_ID}/record`,
    );
  });

  it("offers Re-run failed with the failed and blocked count on a finished run", async () => {
    respondWithRun(
      createRunDetail({
        executor: "claude",
        status: "failed",
        counts: { total: 5, passed: 2, failed: 2, blocked: 1, skipped: 0, notReported: 0 },
      }),
    );

    renderWithProject(<RunManualActions runId={RUN_ID} />, { capabilities: QC_CAPABILITIES });

    expect(
      await screen.findByRole("button", { name: rerun.action.replace("{{count}}", "3") }),
    ).toBeInTheDocument();
  });

  it("renders nothing for a viewer", async () => {
    respondWithRun(createRunDetail({ executor: "claude", status: "failed" }));

    renderWithProject(<RunManualActions runId={RUN_ID} />);

    await vi.waitFor(() => {
      expect(apiGet).toHaveBeenCalled();
    });
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  it("opens the re-run dialog from the keyboard, has no axe violations and returns focus on Escape", async () => {
    const user = userEvent.setup();
    respondWithRun(
      createRunDetail({
        executor: "claude",
        status: "failed",
        counts: { total: 5, passed: 2, failed: 2, blocked: 1, skipped: 0, notReported: 0 },
      }),
    );
    const { container } = renderWithProject(<RunManualActions runId={RUN_ID} />, {
      capabilities: QC_CAPABILITIES,
    });

    const trigger = await screen.findByRole("button", {
      name: rerun.action.replace("{{count}}", "3"),
    });
    expect(await axe(container)).toHaveNoViolations();
    await tabTo(user, trigger);
    await user.keyboard("{Enter}");

    const dialog = await screen.findByRole("dialog", { name: rerun.claudeTitle });
    expect(await axe(dialog)).toHaveNoViolations();
    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
    await waitFor(() => {
      expect(trigger).toHaveFocus();
    });
  });
});
