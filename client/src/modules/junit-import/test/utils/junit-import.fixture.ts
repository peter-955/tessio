import type { JunitImport } from "../../typing/types/junit-import.type";

export const IMPORTED_RUN_ID = "a6000000-0000-4000-8000-0000000000c1";

export const STAGING_ID = "e6000000-0000-4000-8000-000000000001";

export const PRODUCTION_ID = "e6000000-0000-4000-8000-000000000002";

export const SUITE_ID = "5a000000-0000-4000-8000-000000000001";

export const buildEnvironment = (id: string, name: string) => {
  return {
    id,
    name,
    baseUrl: `https://${name.toLowerCase()}.shop.test`,
    healthCheckUrl: null,
    isArchived: false,
    archivedAt: null,
    createdAt: "2026-10-01T09:00:00Z",
  };
};

export const buildJunitImport = (overrides: Partial<JunitImport> = {}): JunitImport => {
  return {
    runId: IMPORTED_RUN_ID,
    status: "failed",
    counts: { total: 3, passed: 1, failed: 1, blocked: 0, skipped: 1, notReported: 0 },
    mappedTestCount: 4,
    unmappedTestCount: 2,
    unmappedTests: [
      {
        name: "loads the home page",
        classname: "home.spec.ts",
        status: "passed",
        reason: "no_case_code",
      },
      { name: "TC-99 refunds", classname: null, status: "failed", reason: "unknown_case" },
    ],
    ...overrides,
  };
};
