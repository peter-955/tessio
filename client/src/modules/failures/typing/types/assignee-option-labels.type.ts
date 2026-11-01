import type { ProjectRole } from "@/components/project-context/typing/types/project.type";

export interface AssignOptionLabels {
  unassigned: string;
  formatRole: (role: ProjectRole) => string;
}

export interface AssigneeFilterLabels {
  anyone: string;
  unassigned: string;
  me: string;
  formatDeactivated: (name: string) => string;
}
