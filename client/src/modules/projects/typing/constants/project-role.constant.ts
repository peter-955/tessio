import type { ProjectRole } from "@/components/project-context/typing/types/project.type";

export const PROJECT_ROLES: ProjectRole[] = ["admin", "pm", "ba", "qc", "dev", "viewer"];

export const DEFAULT_MEMBER_ROLE: ProjectRole = "qc";
