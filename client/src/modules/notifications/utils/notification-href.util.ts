import type { Notification } from "../typing/types/notification.type";

export const buildNotificationHref = (notification: Notification): string => {
  const { payload } = notification;
  const projectPath = `/projects/${encodeURIComponent(notification.projectKey)}`;

  switch (payload.kind) {
    case "gap_assigned":
      return `${projectPath}/stories/${encodeURIComponent(payload.storyJiraKey)}?tab=gaps`;
    case "failure_assigned":
      return `${projectPath}/failures/${encodeURIComponent(payload.failureId)}`;
    case "run_finished":
      return `${projectPath}/runs/${encodeURIComponent(payload.runId)}`;
    default:
      payload satisfies never;
      return projectPath;
  }
};
