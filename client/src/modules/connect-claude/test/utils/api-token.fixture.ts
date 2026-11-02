import type { Project } from "@/components/project-context/typing/types/project.type";
import type { ApiToken, CreatedApiToken } from "../../typing/types/api-token.type";

export const createApiToken = (changes: Partial<ApiToken> = {}): ApiToken => {
  return {
    id: "1b6f0c1e-0c2d-4c4e-9f57-6a5d2b1e7c01",
    name: "My laptop",
    prefix: "a1b2c3d4",
    projectId: "2c7e1d2f-1d3e-4d5f-8a68-7b6e3c2f8d02",
    projectKey: "TES",
    projectName: "Tessio",
    status: "active",
    scope: "mcp",
    expiresAt: "2026-12-01T10:00:00Z",
    lastUsedAt: null,
    pluginVersion: null,
    revokedAt: null,
    createdAt: "2026-11-01T10:00:00Z",
    ...changes,
  };
};

export const createCreatedApiToken = (token: string): CreatedApiToken => {
  return { token, apiToken: createApiToken() };
};

export const createProject = (changes: Partial<Project> = {}): Project => {
  return {
    id: "2c7e1d2f-1d3e-4d5f-8a68-7b6e3c2f8d02",
    key: "TES",
    name: "Tessio",
    description: null,
    jiraProjectKey: "TES",
    jiraBoardId: 1,
    isLinkedToJira: true,
    allowedFileTypes: ["image/png"],
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T10:00:00Z",
    myRole: "qc",
    capabilities: ["project.view"],
    defaultEnvironmentId: null,
    requireSeparateReviewer: false,
    ...changes,
  };
};
