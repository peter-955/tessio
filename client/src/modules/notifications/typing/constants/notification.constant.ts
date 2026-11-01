import type { DSIconName } from "@/components/design-system";
import type { NotificationFilter, NotificationKind } from "../types/notification.type";

export const NOTIFICATION_PAGE_SIZE = 20;

export const MAX_DISPLAYED_UNREAD_COUNT = 99;

export const RELATIVE_TIME_MAXIMUM_DAYS = 7;

export const SECONDS_PER_MINUTE = 60;

export const MINUTES_PER_HOUR = 60;

export const HOURS_PER_DAY = 24;

export const MILLISECONDS_PER_SECOND = 1000;

export const NOTIFICATION_SKELETON_ROW_INDEXES: readonly number[] = [0, 1, 2, 3];

export const NOTIFICATION_SKELETON_ICON_SIZE = 32;

export const NOTIFICATION_KIND_ICON_SIZE = 18;

export const NOTIFICATION_FILTERS: readonly NotificationFilter[] = ["all", "unread"];

export const NOTIFICATION_KIND_ICONS: Record<NotificationKind, DSIconName> = {
  gap_assigned: "infoCircle",
  failure_assigned: "failures",
  run_finished: "runs",
};
