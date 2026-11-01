"use client";

import type { ProjectCapability } from "../typing/types/project.type";
import { checkHasProjectCapability } from "../utils/project-capability.util";
import { useCurrentProject } from "./use-current-project";

export const useHasProjectCapability = (capability: ProjectCapability): boolean => {
  const project = useCurrentProject();

  return checkHasProjectCapability(project, capability);
};
