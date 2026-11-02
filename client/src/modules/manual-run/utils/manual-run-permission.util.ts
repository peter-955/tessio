import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { ManualRunActionsRun } from "../typing/types/manual-run-actions-run.type";

type PermissionProject = Pick<Project, "capabilities" | "isArchived">;

type RecordableRun = Pick<ManualRunActionsRun, "executor" | "status" | "startedBy">;

type RerunnableRun = Pick<
  ManualRunActionsRun,
  "executor" | "status" | "failedCount" | "blockedCount" | "isUntargeted"
>;

const checkCanRecordManually = (project: PermissionProject): boolean => {
  return !project.isArchived && checkHasProjectCapability(project, "run.record_manual");
};

export const checkCanStartManualRun = (project: PermissionProject): boolean => {
  return checkCanRecordManually(project) && checkHasProjectCapability(project, "run.start");
};

export const checkCanRecordRun = (
  project: PermissionProject,
  run: RecordableRun,
  userId: string,
): boolean => {
  return (
    checkCanRecordManually(project) &&
    run.executor === "manual" &&
    run.status === "running" &&
    (run.startedBy === userId || checkHasProjectCapability(project, "run.finish_any"))
  );
};

export const checkCanRevealRunSecrets = (
  project: PermissionProject,
  run: Pick<ManualRunActionsRun, "startedBy">,
  userId: string,
): boolean => {
  return (
    !project.isArchived &&
    checkHasProjectCapability(project, "secret.use_in_run") &&
    run.startedBy === userId
  );
};

export const checkCanRerunFailed = (project: PermissionProject, run: RerunnableRun): boolean => {
  if (project.isArchived || !checkHasProjectCapability(project, "run.start")) {
    return false;
  }

  if (run.status === "running" || run.failedCount + run.blockedCount === 0) {
    return false;
  }

  if (run.isUntargeted === true) {
    return false;
  }

  return run.executor === "claude" || checkHasProjectCapability(project, "run.record_manual");
};
