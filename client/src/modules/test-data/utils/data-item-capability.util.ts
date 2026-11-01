import type { Project } from "@/components/project-context/typing/types/project.type";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import type { DataItemKind } from "../typing/types/data-item.type";

export const canEditDataItemKinds = (
  project: Pick<Project, "capabilities">,
  kinds: readonly DataItemKind[],
): boolean => {
  if (!checkHasProjectCapability(project, "test_data.edit")) {
    return false;
  }

  return !kinds.includes("secret") || checkHasProjectCapability(project, "secret.edit");
};
