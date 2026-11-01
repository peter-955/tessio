import { describe, expect, it } from "vitest";
import {
  buildEnvironment,
  LEGACY_ENVIRONMENT_ID,
  PRODUCTION_ENVIRONMENT_ID,
  STAGING_ENVIRONMENT_ID,
} from "../test/utils/test-data-fixture.util";
import { PROJECT_SCOPE_ID } from "../typing/constants/test-data.constant";
import { buildDataGridColumns } from "./build-data-grid-columns.util";

const legacy = buildEnvironment({
  id: LEGACY_ENVIRONMENT_ID,
  name: "Legacy",
  isArchived: true,
  archivedAt: "2026-10-02T09:00:00Z",
});
const production = buildEnvironment({ id: PRODUCTION_ENVIRONMENT_ID, name: "Production" });
const staging = buildEnvironment();

describe("buildDataGridColumns", () => {
  it("puts the project column first, then the active environments", () => {
    const columns = buildDataGridColumns([legacy, production, staging], false);

    expect(columns.map((column) => column.scopeId)).toEqual([
      PROJECT_SCOPE_ID,
      PRODUCTION_ENVIRONMENT_ID,
      STAGING_ENVIRONMENT_ID,
    ]);
    expect(columns[0]).toEqual({ scopeId: PROJECT_SCOPE_ID, environment: null, isArchived: false });
  });

  it("adds archived environments last when the toggle is on", () => {
    const columns = buildDataGridColumns([legacy, production, staging], true);

    expect(columns.map((column) => column.scopeId)).toEqual([
      PROJECT_SCOPE_ID,
      PRODUCTION_ENVIRONMENT_ID,
      STAGING_ENVIRONMENT_ID,
      LEGACY_ENVIRONMENT_ID,
    ]);
    expect(columns.at(-1)?.isArchived).toBe(true);
  });

  it("keeps the project column without environments", () => {
    expect(buildDataGridColumns([], true)).toHaveLength(1);
  });
});
