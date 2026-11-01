import type { Project } from "@/components/project-context/typing/types/project.type";
import type { ArchiveMode } from "./archive-mode.type";

export interface ArchiveTarget {
  project: Pick<Project, "key" | "name">;
  mode: ArchiveMode;
}
