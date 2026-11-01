import type { ProjectSyncStatus } from "../types/story.type";

export const SYNC_STATUS_POLL_INTERVAL_IN_MILLISECONDS = 5000;

export const SYNC_STALE_AFTER_IN_MILLISECONDS = 900000;

export const IN_PROGRESS_SYNC_STATUSES: ProjectSyncStatus[] = ["queued", "running"];

export const MISSING_SYNC_DATE = "—";
