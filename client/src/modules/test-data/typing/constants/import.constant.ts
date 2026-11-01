import type { DSBadgeColor } from "@/components/design-system";
import type { ImportAction } from "../types/import.type";

export const IMPORT_ACTION_BADGE_COLORS: Record<ImportAction, DSBadgeColor> = {
  create: "green",
  update: "yellow",
  unchanged: "gray",
};
