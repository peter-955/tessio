import type { components } from "@/lib/api/openapi.type";

export type Notification = components["schemas"]["NotificationResponse"];

export type NotificationPage = components["schemas"]["NotificationPageResponse"];

export type NotificationKind = components["schemas"]["NotificationKind"];

export type RunOutcome = components["schemas"]["RunOutcome"];

export type NotificationPayload = Notification["payload"];

export type ReportReadyPayload = components["schemas"]["ReportReadyPayloadResponse"];

export type UnreadNotificationCount = components["schemas"]["UnreadNotificationCountResponse"];

export type NotificationFilter = "all" | "unread";

export interface NotificationDescription {
  title: string;
  description: string;
}
