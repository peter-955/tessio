import type { AssignableRole } from "./gap.type";

export interface AssigneeOptionLabels {
  formatRole: (role: AssignableRole) => string;
  formatAnyRole: (role: AssignableRole) => string;
}
