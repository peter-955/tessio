import type { DSBadgeColor } from "@/components/design-system";
import type { LabelColor } from "../types/label.type";

export const LABEL_COLORS: readonly LabelColor[] = [
  "gray",
  "red",
  "orange",
  "yellow",
  "green",
  "teal",
  "blue",
  "violet",
];

export const DEFAULT_LABEL_COLOR: LabelColor = "gray";

export const LABEL_BADGE_COLORS: Record<LabelColor, DSBadgeColor> = {
  gray: "gray",
  red: "red",
  orange: "orange",
  yellow: "yellow",
  green: "green",
  teal: "teal",
  blue: "blue",
  violet: "violet",
};

export const MAX_LABEL_NAME_LENGTH = 40;

export const MAX_LABELS_PER_CASE = 20;

export const LABEL_PARAMETER = "label";
