import type { DSBadgeColor } from "@/components/design-system";
import type { PluginState } from "../types/plugin-state.type";

export const PLUGIN_STATE_BADGE_COLOR: Record<PluginState, DSBadgeColor> = {
  current: "green",
  outdated: "yellow",
  unused: "gray",
};
