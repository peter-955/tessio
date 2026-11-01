"use client";

import { use } from "react";
import { ProjectContext } from "../contexts/project.context";
import type { Project } from "../typing/types/project.type";

export const useCurrentProject = (): Project => {
  const project = use(ProjectContext);

  if (project === null) {
    throw new Error("useCurrentProject must be used inside ProjectGate");
  }

  return project;
};
