import type {
  Project,
  ProjectCapability,
} from "@/components/project-context/typing/types/project.type";

export const VIEWER_CAPABILITIES: ProjectCapability[] = [
  "project.view",
  "test_data.view",
  "run.view",
];

export const ADMIN_CAPABILITIES: ProjectCapability[] = [
  ...VIEWER_CAPABILITIES,
  "project.edit",
  "environment.manage",
  "test_data.edit",
  "secret.edit",
  "secret.reveal",
];

export const buildProject = (overrides: Partial<Project> = {}): Project => {
  return {
    id: "6f1c1d3e-8a59-4a39-9a43-1c6f0b3f2a10",
    key: "SHOP",
    name: "Shop",
    description: null,
    jiraProjectKey: "SHOP",
    jiraBoardId: 1,
    isLinkedToJira: true,
    allowedFileTypes: ["text/plain", "application/json"],
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
    myRole: "viewer",
    capabilities: VIEWER_CAPABILITIES,
    defaultEnvironmentId: null,
    requireSeparateReviewer: false,
    ...overrides,
  };
};
