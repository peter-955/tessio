import type { DSAlign, DSJustify } from "../types/layout.type";

export const DS_ALIGN_VALUES: Record<DSAlign, string> = {
  start: "flex-start",
  center: "center",
  end: "flex-end",
  baseline: "baseline",
  stretch: "stretch",
};

export const DS_JUSTIFY_VALUES: Record<DSJustify, string> = {
  start: "flex-start",
  center: "center",
  end: "flex-end",
  between: "space-between",
};
