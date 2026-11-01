import { describe, expect, it } from "vitest";
import { buildDataItem, STAGING_ENVIRONMENT_ID } from "../test/utils/test-data-fixture.util";
import { PROJECT_SCOPE_ID } from "../typing/constants/test-data.constant";
import { buildDataGridRows, filterDataGridRows, findRowKind } from "./build-data-grid-rows.util";

const projectItem = buildDataItem({ id: "item-1", key: "API_URL", kind: "endpoint" });
const stagingItem = buildDataItem({
  id: "item-2",
  key: "API_URL",
  kind: "endpoint",
  environmentId: STAGING_ENVIRONMENT_ID,
});
const passwordItem = buildDataItem({
  id: "item-3",
  key: "PASSWORD",
  kind: "secret",
  value: null,
  environmentId: STAGING_ENVIRONMENT_ID,
});

describe("buildDataGridRows", () => {
  it("groups items by key in server order and indexes them by scope", () => {
    const rows = buildDataGridRows([projectItem, stagingItem, passwordItem]);

    expect(rows.map((row) => row.key)).toEqual(["API_URL", "PASSWORD"]);
    expect(rows[0]?.itemByScopeId).toEqual({
      [PROJECT_SCOPE_ID]: projectItem,
      [STAGING_ENVIRONMENT_ID]: stagingItem,
    });
    expect(rows[1]?.itemByScopeId).toEqual({ [STAGING_ENVIRONMENT_ID]: passwordItem });
  });

  it("returns no rows without items", () => {
    expect(buildDataGridRows([])).toEqual([]);
  });
});

describe("findRowKind", () => {
  it("prefers the kind of the project item", () => {
    const [row] = buildDataGridRows([
      buildDataItem({ key: "TOKEN", kind: "variable" }),
      buildDataItem({ key: "TOKEN", kind: "secret", environmentId: STAGING_ENVIRONMENT_ID }),
    ]);

    expect(row && findRowKind(row)).toBe("variable");
  });

  it("falls back to the first environment item", () => {
    const [row] = buildDataGridRows([passwordItem]);

    expect(row && findRowKind(row)).toBe("secret");
  });
});

describe("filterDataGridRows", () => {
  const rows = buildDataGridRows([projectItem, passwordItem]);

  it("filters keys case-insensitively", () => {
    expect(filterDataGridRows(rows, " pass ").map((row) => row.key)).toEqual(["PASSWORD"]);
  });

  it("keeps every row for an empty search", () => {
    expect(filterDataGridRows(rows, "")).toHaveLength(2);
  });
});
