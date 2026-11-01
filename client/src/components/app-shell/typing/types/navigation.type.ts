import type { DSIconName } from "@/components/design-system";
import type { components } from "@/lib/api/openapi.type";
import type { LocaleResources } from "@/lib/i18n/typing/types/locale.type";

export interface ProjectNavigationItem {
  segment: string;
  labelKey: keyof LocaleResources["navigation"];
  icon: DSIconName;
  capability: components["schemas"]["Capability"];
}

export interface WorkspaceNavigationItem {
  href: string;
  labelKey: keyof LocaleResources["navigation"];
  icon: DSIconName;
  isWorkspaceAdminOnly: boolean;
}
