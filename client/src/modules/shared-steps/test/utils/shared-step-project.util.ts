import {
  ADMIN_CAPABILITIES,
  VIEWER_CAPABILITIES,
} from "@/components/project-context/test/utils/project-fixture.util";
import type {
  Project,
  ProjectCapability,
} from "@/components/project-context/typing/types/project.type";

export const QC_CAPABILITIES: ProjectCapability[] = [...VIEWER_CAPABILITIES, "test_case.edit"];

export const QC_PROJECT: Partial<Project> = { myRole: "qc", capabilities: QC_CAPABILITIES };

export const ADMIN_PROJECT: Partial<Project> = {
  myRole: "admin",
  capabilities: ADMIN_CAPABILITIES,
};

export const VIEWER_PROJECT: Partial<Project> = {
  myRole: "viewer",
  capabilities: VIEWER_CAPABILITIES,
};
