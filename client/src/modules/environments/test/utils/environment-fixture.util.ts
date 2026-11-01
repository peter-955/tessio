import type { Environment } from "../../typing/types/environment.type";

export const buildEnvironment = (overrides: Partial<Environment> = {}): Environment => {
  return {
    id: "1b7d1f0e-5a43-4c55-9d0b-0c2b6a0e4f11",
    name: "Staging",
    baseUrl: "https://staging.example.test",
    healthCheckUrl: "https://staging.example.test/health",
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};
