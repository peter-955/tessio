import { describe, expect, it } from "vitest";
import { buildImportItem } from "../test/utils/test-case-fixture.util";
import {
  buildCaseImportRows,
  includeAllCaseImportRows,
  readIncludedCaseImportIndexes,
  toggleCaseImportRow,
} from "./import-rows.util";

const ITEMS = [
  buildImportItem({ index: 0 }),
  buildImportItem({ index: 1, isDuplicate: true }),
  buildImportItem({ index: 2, problem: "story_not_found" }),
];

describe("import rows", () => {
  it("leaves duplicates unchecked and blocks rows with a problem", () => {
    expect(
      buildCaseImportRows(ITEMS).map((row) => [row.item.index, row.isSelectable, row.isIncluded]),
    ).toEqual([
      [0, true, true],
      [1, true, false],
      [2, false, false],
    ]);
  });

  it("selects all selectable rows and toggles one", () => {
    const rows = buildCaseImportRows(ITEMS);

    expect(readIncludedCaseImportIndexes(includeAllCaseImportRows(rows, true))).toEqual([0, 1]);
    expect(readIncludedCaseImportIndexes(includeAllCaseImportRows(rows, false))).toEqual([]);
    expect(readIncludedCaseImportIndexes(toggleCaseImportRow(rows, 1, true))).toEqual([0, 1]);
    expect(readIncludedCaseImportIndexes(toggleCaseImportRow(rows, 2, true))).toEqual([0]);
  });
});
