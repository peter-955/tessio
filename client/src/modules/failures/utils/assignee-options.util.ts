import type { DSSelectOption } from "@/components/design-system";
import type { ProjectMember } from "@/components/project-context/typing/types/project.type";
import {
  ANY_ASSIGNEE_OPTION,
  ME_FILTER,
  UNASSIGNED_FILTER,
  UNASSIGNED_OPTION,
} from "../typing/constants/failure.constant";
import type {
  AssigneeFilterLabels,
  AssignOptionLabels,
} from "../typing/types/assignee-option-labels.type";

const sortMembersByName = (members: ProjectMember[]): ProjectMember[] => {
  return [...members].sort((first, second) => {
    return first.name.localeCompare(second.name);
  });
};

export const buildAssignOptions = (
  members: ProjectMember[],
  labels: AssignOptionLabels,
): DSSelectOption<string>[] => {
  const activeMembers = members.filter((member) => {
    return member.userStatus === "active";
  });
  const memberOptions = sortMembersByName(activeMembers).map((member): DSSelectOption<string> => {
    return { value: member.userId, label: `${member.name} · ${labels.formatRole(member.role)}` };
  });

  return [{ value: UNASSIGNED_OPTION, label: labels.unassigned }, ...memberOptions];
};

export const buildAssigneeFilterOptions = (
  members: ProjectMember[],
  labels: AssigneeFilterLabels,
): DSSelectOption<string>[] => {
  const memberOptions = sortMembersByName(members).map((member): DSSelectOption<string> => {
    return {
      value: member.userId,
      label:
        member.userStatus === "deactivated" ? labels.formatDeactivated(member.name) : member.name,
    };
  });

  return [
    { value: ANY_ASSIGNEE_OPTION, label: labels.anyone },
    { value: UNASSIGNED_FILTER, label: labels.unassigned },
    { value: ME_FILTER, label: labels.me },
    ...memberOptions,
  ];
};
