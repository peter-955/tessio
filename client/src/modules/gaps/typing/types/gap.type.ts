import type { ProjectRole } from "@/components/project-context/typing/types/project.type";
import type { components } from "@/lib/api/openapi.type";

export type Gap = components["schemas"]["GapResponse"];

export type GapType = components["schemas"]["GapType"];

export type GapSeverity = components["schemas"]["GapSeverity"];

export type GapTargetType = components["schemas"]["GapTargetType"];

export type GapStatus = components["schemas"]["GapStatus"];

export type GapDataScope = components["schemas"]["GapDataScope"];

export type RaiseGapBody = components["schemas"]["RaiseGapRequest"];

export type ReassignGapBody = components["schemas"]["ReassignGapRequest"];

export type GapStatusFilter = "open" | "resolved" | "all";

export type InboxFilter = "open" | "all";

export type AssignableRole = Exclude<ProjectRole, "viewer">;

export type AssigneeChoice =
  { kind: "member"; userId: string } | { kind: "role"; role: AssignableRole };

export type GapAssignee =
  | { kind: "user"; name: string; isDeactivated: boolean }
  | { kind: "role"; role: AssignableRole }
  | { kind: "unassigned" };

export type GapAction = "answer" | "reassign" | "reopen";

export interface GapActionTarget {
  gap: Gap;
  action: GapAction;
}
