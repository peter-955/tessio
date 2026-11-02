import type { DSBadgeColor } from "../typing/types/badge.type";
import type { DSIconName } from "../typing/types/icon.type";
import type { DSStepTimelineStatus, DSStepTimelineStatusStyle } from "./step-timeline.type";

export const DS_STEP_TIMELINE_STATUS_STYLES: Record<
  DSStepTimelineStatus,
  DSStepTimelineStatusStyle
> = {
  passed: { color: "green", icon: "check" },
  failed: { color: "red", icon: "close" },
  blocked: { color: "yellow", icon: "alertCircle" },
  skipped: { color: "gray", icon: "arrowRight" },
  pending: { color: "gray", icon: "dots" },
  not_reported: { color: "gray", icon: "dots" },
};

export const DS_STEP_TIMELINE_NUMBER_COLOR: DSBadgeColor = "tessio";

export const DS_STEP_TIMELINE_EXPECTED_ICON: DSIconName = "circleCheck";

export const DS_STEP_TIMELINE_BULLET_SIZE = 24;

export const DS_STEP_TIMELINE_LINE_WIDTH = 2;

export const DS_STEP_TIMELINE_ICON_SIZE = 14;
