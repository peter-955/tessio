import type { DSBadgeColor } from "../types/badge.type";

export const DS_BADGE_TEXT_COLORS: Record<DSBadgeColor, string | undefined> = {
  gray: undefined,
  tessio: undefined,
  green: "var(--color-green-text)",
  red: "var(--color-red-text)",
  yellow: "var(--color-yellow-text)",
  orange: "var(--color-orange-text)",
  teal: "var(--color-teal-text)",
  blue: "var(--color-blue-text)",
  violet: "var(--color-violet-text)",
};
