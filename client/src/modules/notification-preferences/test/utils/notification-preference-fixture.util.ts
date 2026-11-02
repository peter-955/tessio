import type { NotificationPreference } from "../../typing/types/notification-preference.type";

export const buildDefaultNotificationPreferences = (): NotificationPreference[] => {
  return [
    { kind: "gap_assigned", inApp: true, email: true },
    { kind: "failure_assigned", inApp: true, email: true },
    { kind: "run_finished", inApp: true, email: false },
    { kind: "suite_run_finished", inApp: true, email: false },
    { kind: "report_ready", inApp: true, email: false },
  ];
};
