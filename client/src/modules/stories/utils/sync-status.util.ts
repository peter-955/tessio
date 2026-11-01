import {
  IN_PROGRESS_SYNC_STATUSES,
  SYNC_STALE_AFTER_IN_MILLISECONDS,
} from "../typing/constants/sync.constant";
import type { ProjectSyncState } from "../typing/types/story.type";

const checkIsSyncActive = (state: ProjectSyncState | undefined): state is ProjectSyncState => {
  return state !== undefined && IN_PROGRESS_SYNC_STATUSES.includes(state.status);
};

export const checkIsSyncInProgress = (state: ProjectSyncState | undefined, now: Date): boolean => {
  if (!checkIsSyncActive(state)) {
    return false;
  }

  const startedAt = state.startedAt ?? state.queuedAt;
  if (startedAt === null) {
    return false;
  }

  return new Date(startedAt).getTime() > now.getTime() - SYNC_STALE_AFTER_IN_MILLISECONDS;
};

export const checkIsSyncStale = (state: ProjectSyncState | undefined, now: Date): boolean => {
  return checkIsSyncActive(state) && !checkIsSyncInProgress(state, now);
};
