import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";

type ProjectAccess = Pick<Project, "capabilities">;

export const checkCanExportReport = (project: ProjectAccess): boolean => {
  return checkHasProjectCapability(project, "report.view");
};

export const checkCanDownloadReport = (project: ProjectAccess): boolean => {
  return checkHasProjectCapability(project, "file.download");
};
