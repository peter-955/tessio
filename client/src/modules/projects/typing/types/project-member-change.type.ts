import type { ProjectRole } from "@/components/project-context/typing/types/project.type";

export interface ProjectMemberChange {
  userId: string;
  role: ProjectRole;
}
