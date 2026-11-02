import type { DSBadgeColor, DSIconName } from "@/components/design-system";
import type { FlakyCaseFlags } from "./flaky-case-flags.type";

export type FlakyCaseBadgeKind = "flaky" | "disagreeing" | "quarantined";

export interface FlakyCaseBadgeDefinition {
  kind: FlakyCaseBadgeKind;
  flag: keyof FlakyCaseFlags;
  icon: DSIconName;
  color: DSBadgeColor;
}
