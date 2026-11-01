import type { DSBadgeColor } from "@/components/design-system";
import type { SprintState } from "../types/sprint.type";

export const SPRINT_STATE_COLORS: Record<SprintState, DSBadgeColor> = {
  active: "green",
  future: "tessio",
  closed: "gray",
};

export const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const NOT_FOUND_STATUSES: readonly number[] = [404, 422];

export const MISSING_SPRINT_DATE = "?";
