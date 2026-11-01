import type { DSBadgeColor } from "@/components/design-system";
import type { ApiTokenStatus } from "../types/api-token.type";

export const TOKEN_STATUS_BADGE_COLOR: Record<ApiTokenStatus, DSBadgeColor> = {
  active: "green",
  expired: "gray",
  revoked: "red",
};
