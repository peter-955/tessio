import type {
  Project,
  ProjectCapability,
} from "@/components/project-context/typing/types/project.type";

export const VIEWER_CAPABILITIES: ProjectCapability[] = [
  "project.view",
  "story.view",
  "test_case.view",
  "run.view",
  "failure.view",
  "file.download",
];

export const DEV_CAPABILITIES: ProjectCapability[] = [
  ...VIEWER_CAPABILITIES,
  "failure.assign",
  "failure.mark_fixed",
];

export const QC_CAPABILITIES: ProjectCapability[] = [
  ...VIEWER_CAPABILITIES,
  "test_case.edit",
  "failure.assign",
  "failure.verify",
];

export const buildProject = (overrides: Partial<Project> = {}): Project => {
  return {
    id: "6f1c1d3e-8a59-4a39-9a43-1c6f0b3f2a10",
    key: "SHOP",
    name: "Shop",
    description: null,
    jiraProjectKey: "SHOP",
    jiraBoardId: 1,
    allowedFileTypes: ["text/plain"],
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
    myRole: "viewer",
    capabilities: VIEWER_CAPABILITIES,
    defaultEnvironmentId: null,
    ...overrides,
  };
};
