import { VIEWER_CAPABILITIES } from "@/components/project-context/test/utils/project-fixture.util";
import { describe, expect, it } from "vitest";
import {
  ADMIN_CAPABILITIES,
  CURRENT_USER_ID,
  OTHER_USER_ID,
  QC_CAPABILITIES,
  buildRunProject,
} from "../test/utils/run.fixture";
import type { ManualRunActionsRun } from "../typing/types/manual-run-actions-run.type";
import {
  checkCanRecordRun,
  checkCanRerunFailed,
  checkCanStartManualRun,
} from "./manual-run-permission.util";

const RUNNING_RUN: ManualRunActionsRun = {
  id: "d1000000-0000-4000-8000-000000000001",
  executor: "manual",
  status: "running",
  startedBy: CURRENT_USER_ID,
  failedCount: 0,
  blockedCount: 0,
};

const FINISHED_RUN: ManualRunActionsRun = {
  ...RUNNING_RUN,
  status: "failed",
  failedCount: 1,
  blockedCount: 1,
};

describe("checkCanStartManualRun", () => {
  it("needs run.start and run.record_manual on an active project", () => {
    expect(checkCanStartManualRun(buildRunProject())).toBe(true);
    expect(checkCanStartManualRun(buildRunProject({ capabilities: VIEWER_CAPABILITIES }))).toBe(
      false,
    );
    expect(
      checkCanStartManualRun(
        buildRunProject({ capabilities: [...VIEWER_CAPABILITIES, "run.start"] }),
      ),
    ).toBe(false);
    expect(checkCanStartManualRun(buildRunProject({ isArchived: true }))).toBe(false);
  });
});

describe("checkCanRecordRun", () => {
  it("lets the starter record a running manual run", () => {
    expect(checkCanRecordRun(buildRunProject(), RUNNING_RUN, CURRENT_USER_ID)).toBe(true);
  });

  it("needs run.finish_any for somebody else's run", () => {
    const run = { ...RUNNING_RUN, startedBy: OTHER_USER_ID };

    expect(checkCanRecordRun(buildRunProject(), run, CURRENT_USER_ID)).toBe(false);
    expect(
      checkCanRecordRun(
        buildRunProject({ capabilities: ADMIN_CAPABILITIES }),
        run,
        CURRENT_USER_ID,
      ),
    ).toBe(true);
  });

  it("refuses Claude runs, finished runs, viewers and archived projects", () => {
    expect(
      checkCanRecordRun(buildRunProject(), { ...RUNNING_RUN, executor: "claude" }, CURRENT_USER_ID),
    ).toBe(false);
    expect(
      checkCanRecordRun(buildRunProject(), { ...RUNNING_RUN, status: "passed" }, CURRENT_USER_ID),
    ).toBe(false);
    expect(
      checkCanRecordRun(
        buildRunProject({ capabilities: VIEWER_CAPABILITIES }),
        RUNNING_RUN,
        CURRENT_USER_ID,
      ),
    ).toBe(false);
    expect(
      checkCanRecordRun(buildRunProject({ isArchived: true }), RUNNING_RUN, CURRENT_USER_ID),
    ).toBe(false);
  });

  it("does not need run.start to record", () => {
    const capabilities = QC_CAPABILITIES.filter((capability) => capability !== "run.start");

    expect(checkCanRecordRun(buildRunProject({ capabilities }), RUNNING_RUN, CURRENT_USER_ID)).toBe(
      true,
    );
  });
});

describe("checkCanRerunFailed", () => {
  it("allows a finished manual run with failed or blocked cases", () => {
    expect(checkCanRerunFailed(buildRunProject(), FINISHED_RUN)).toBe(true);
    expect(
      checkCanRerunFailed(buildRunProject(), { ...FINISHED_RUN, failedCount: 0, blockedCount: 1 }),
    ).toBe(true);
  });

  it("hides the re-run for running runs and runs without failures", () => {
    expect(checkCanRerunFailed(buildRunProject(), { ...FINISHED_RUN, status: "running" })).toBe(
      false,
    );
    expect(
      checkCanRerunFailed(buildRunProject(), { ...FINISHED_RUN, failedCount: 0, blockedCount: 0 }),
    ).toBe(false);
  });

  it("needs run.start on an active project", () => {
    expect(
      checkCanRerunFailed(buildRunProject({ capabilities: VIEWER_CAPABILITIES }), FINISHED_RUN),
    ).toBe(false);
    expect(checkCanRerunFailed(buildRunProject({ isArchived: true }), FINISHED_RUN)).toBe(false);
  });

  it("needs run.record_manual for manual runs only", () => {
    const project = buildRunProject({ capabilities: [...VIEWER_CAPABILITIES, "run.start"] });

    expect(checkCanRerunFailed(project, FINISHED_RUN)).toBe(false);
    expect(checkCanRerunFailed(project, { ...FINISHED_RUN, executor: "claude" })).toBe(true);
  });
});
