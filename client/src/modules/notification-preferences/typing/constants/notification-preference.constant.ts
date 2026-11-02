import type { NotificationPreferenceKind } from "../types/notification-preference.type";

export const NOTIFICATION_PREFERENCE_KIND_KEYS = {
  gap_assigned: "gapAssigned",
  failure_assigned: "failureAssigned",
  run_finished: "runFinished",
  suite_run_finished: "suiteRunFinished",
  report_ready: "reportReady",
} as const satisfies Readonly<Record<NotificationPreferenceKind, string>>;
