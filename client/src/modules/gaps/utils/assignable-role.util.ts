import { ASSIGNABLE_ROLES } from "../typing/constants/gap.constant";
import type { AssignableRole } from "../typing/types/gap.type";

export const checkIsAssignableRole = (role: string): role is AssignableRole => {
  return ASSIGNABLE_ROLES.some((assignableRole) => {
    return assignableRole === role;
  });
};
