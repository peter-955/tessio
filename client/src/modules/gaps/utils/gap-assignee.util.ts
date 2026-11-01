import type { Gap, GapAssignee } from "../typing/types/gap.type";
import { checkIsAssignableRole } from "./assignable-role.util";

export const describeAssignee = (gap: Gap): GapAssignee => {
  if (gap.assigneeId !== null && gap.assigneeName !== null) {
    return {
      kind: "user",
      name: gap.assigneeName,
      isDeactivated: gap.assigneeStatus === "deactivated",
    };
  }

  if (gap.assigneeRole !== null && checkIsAssignableRole(gap.assigneeRole)) {
    return { kind: "role", role: gap.assigneeRole };
  }

  return { kind: "unassigned" };
};
