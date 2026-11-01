import type { DSTextColor, DSTextWeight, DSTitleType } from "../types/text.type";

export const DS_TEXT_COLORS: Record<DSTextColor, string | undefined> = {
  default: undefined,
  muted: "var(--color-text-muted)",
  danger: "var(--color-danger)",
  success: "var(--color-success)",
  warning: "var(--color-warning)",
};

export const DS_TEXT_WEIGHTS: Record<DSTextWeight, number> = {
  regular: 400,
  medium: 500,
};

export const DS_TITLE_SIZES: Record<DSTitleType, string> = {
  page: "var(--text-xl)",
  section: "var(--text-md)",
};
