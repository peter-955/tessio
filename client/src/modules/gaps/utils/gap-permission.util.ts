import type { ProjectRole } from "@/components/project-context/typing/types/project.type";
import { REOPENING_ROLES } from "../typing/constants/gap.constant";
import type { Gap } from "../typing/types/gap.type";

export const canReopenGap = (
  gap: Pick<Gap, "status" | "raisedBy">,
  currentUserId: string,
  myRole: ProjectRole | null,
  canRaise: boolean,
): boolean => {
  if (!canRaise || gap.status !== "resolved") {
    return false;
  }

  return gap.raisedBy === currentUserId || (myRole !== null && REOPENING_ROLES.includes(myRole));
};
