import type { DSBadgeColor } from "@/components/design-system";
import type { CompareRowKind } from "../types/version-comparison.type";

export const COMPARE_ROW_KIND_COLORS: Record<CompareRowKind, DSBadgeColor> = {
  unchanged: "gray",
  changed: "yellow",
  added: "green",
  removed: "red",
};
