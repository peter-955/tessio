import type { DSSelectOption } from "@/components/design-system";
import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import {
  ASSIGNABLE_ROLES,
  MEMBER_CHOICE_PREFIX,
  ROLE_CHOICE_PREFIX,
} from "../typing/constants/gap.constant";
import type { AssigneeOptionLabels } from "../typing/types/assignee-option-labels.type";
import type { AssigneeChoice, Gap, ReassignGapBody } from "../typing/types/gap.type";
import { checkIsAssignableRole } from "./assignable-role.util";

export const buildMemberOptions = (
  members: ProjectMember[],
  formatRole: AssigneeOptionLabels["formatRole"],
  valuePrefix = "",
): DSSelectOption<string>[] => {
  return members.flatMap((member): DSSelectOption<string>[] => {
    if (member.userStatus !== "active" || !checkIsAssignableRole(member.role)) {
      return [];
    }

    return [
      {
        value: `${valuePrefix}${member.userId}`,
        label: `${member.name} · ${formatRole(member.role)}`,
      },
    ];
  });
};

export const buildAssigneeOptions = (
  members: ProjectMember[],
  labels: AssigneeOptionLabels,
): DSSelectOption<string>[] => {
  const roleOptions = ASSIGNABLE_ROLES.map((role): DSSelectOption<string> => {
    return { value: `${ROLE_CHOICE_PREFIX}${role}`, label: labels.formatAnyRole(role) };
  });

  return [...buildMemberOptions(members, labels.formatRole, MEMBER_CHOICE_PREFIX), ...roleOptions];
};

export const parseAssigneeChoice = (value: string | null): AssigneeChoice | null => {
  if (value === null) {
    return null;
  }

  if (value.startsWith(MEMBER_CHOICE_PREFIX)) {
    const userId = value.slice(MEMBER_CHOICE_PREFIX.length);

    return userId === "" ? null : { kind: "member", userId };
  }

  if (value.startsWith(ROLE_CHOICE_PREFIX)) {
    const role = value.slice(ROLE_CHOICE_PREFIX.length);

    return checkIsAssignableRole(role) ? { kind: "role", role } : null;
  }

  return null;
};

export const buildAssigneeChoiceValue = (gap: Gap): string | null => {
  if (gap.assigneeId !== null) {
    return `${MEMBER_CHOICE_PREFIX}${gap.assigneeId}`;
  }

  if (gap.assigneeRole !== null && checkIsAssignableRole(gap.assigneeRole)) {
    return `${ROLE_CHOICE_PREFIX}${gap.assigneeRole}`;
  }

  return null;
};

export const buildReassignBody = (choice: AssigneeChoice): ReassignGapBody => {
  return choice.kind === "member" ? { assigneeId: choice.userId } : { assigneeRole: choice.role };
};
