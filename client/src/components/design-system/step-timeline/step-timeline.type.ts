import type { ReactNode } from "react";
import type { DSBadgeColor } from "../typing/types/badge.type";
import type { DSIconName } from "../typing/types/icon.type";

export type DSStepTimelineStatus =
  "passed" | "failed" | "blocked" | "skipped" | "pending" | "not_reported";

export interface DSStepTimelineStep {
  key: string;
  order: number;
  action: string;
  expected: string | null;
  status: DSStepTimelineStatus;
  statusLabel: string;
  actualResult: string | null;
  error: string | null;
  media?: ReactNode;
}

export interface DSStepTimelineLabels {
  step: (order: number) => string;
  expected: string;
  actualResult: string;
  error: string;
}

export interface DSStepTimelineStatusStyle {
  color: DSBadgeColor;
  icon: DSIconName;
}
