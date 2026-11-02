import type { components } from "@/lib/api/openapi.type";

export type NotificationPreference = components["schemas"]["NotificationPreferenceResponse"];

export type NotificationPreferenceKind = components["schemas"]["NotificationKind"];

export type NotificationPreferenceChange =
  components["schemas"]["NotificationPreferenceChangeRequest"];

export type UpdateNotificationPreferencesRequest =
  components["schemas"]["UpdateNotificationPreferencesRequest"];
