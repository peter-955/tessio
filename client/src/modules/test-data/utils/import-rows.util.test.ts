import { describe, expect, it } from "vitest";
import type { ImportPreviewItem } from "../typing/types/import.type";
import { buildImportRows, isImportRowLocked } from "./import-rows.util";

const items: ImportPreviewItem[] = [
  {
    key: "API_URL",
    kind: "variable",
    value: "https://api.example.test",
    action: "create",
    description: "Shop API",
  },
  { key: "USER", kind: "variable", value: "ada", action: "update", description: null },
  { key: "LOCALE", kind: "variable", value: "en", action: "unchanged", description: null },
  { key: "PASSWORD", kind: "secret", value: null, action: "create", description: null },
];

describe("buildImportRows", () => {
  it("includes created and updated rows by default", () => {
    const rows = buildImportRows(items, true);

    expect(rows.map((row) => row.isIncluded)).toEqual([true, true, false, true]);
    expect(rows[3]).toEqual({
      key: "PASSWORD",
      kind: "secret",
      suggestedKind: "secret",
      value: null,
      description: null,
      action: "create",
      isIncluded: true,
    });
  });

  it("excludes suggested secrets without secret.edit", () => {
    const rows = buildImportRows(items, false);

    expect(rows.map((row) => row.isIncluded)).toEqual([true, true, false, false]);
  });
});

describe("isImportRowLocked", () => {
  it("locks suggested secrets only without secret.edit", () => {
    expect(isImportRowLocked({ suggestedKind: "secret" }, false)).toBe(true);
    expect(isImportRowLocked({ suggestedKind: "secret" }, true)).toBe(false);
    expect(isImportRowLocked({ suggestedKind: "variable" }, false)).toBe(false);
  });
});
