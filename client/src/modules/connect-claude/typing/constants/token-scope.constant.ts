import type { DSBadgeColor } from "@/components/design-system";
import type { ApiTokenScope } from "../types/api-token.type";

export const TOKEN_SCOPE_BADGE_COLOR: Record<ApiTokenScope, DSBadgeColor> = {
  mcp: "tessio",
  api: "blue",
};
