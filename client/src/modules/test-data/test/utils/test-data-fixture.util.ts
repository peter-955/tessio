import type { DataItem } from "../../typing/types/data-item.type";
import type { Environment } from "../../typing/types/environment.type";

export const STAGING_ENVIRONMENT_ID = "1b7d1f0e-5a43-4c55-9d0b-0c2b6a0e4f11";

export const PRODUCTION_ENVIRONMENT_ID = "2c8e2a1f-6b54-4d66-8e1c-1d3c7b1f5a22";

export const LEGACY_ENVIRONMENT_ID = "3d9f3b2a-7c65-4e77-9f2d-2e4d8c2a6b33";

export const buildEnvironment = (overrides: Partial<Environment> = {}): Environment => {
  return {
    id: STAGING_ENVIRONMENT_ID,
    name: "Staging",
    baseUrl: "https://staging.example.test",
    healthCheckUrl: null,
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};

export const buildDataItem = (overrides: Partial<DataItem> = {}): DataItem => {
  return {
    id: "a1000000-0000-4000-8000-000000000001",
    environmentId: null,
    key: "BASE_PATH",
    kind: "variable",
    value: "/shop",
    hasValue: true,
    description: null,
    createdAt: "2026-10-01T09:00:00Z",
    ...overrides,
  };
};
