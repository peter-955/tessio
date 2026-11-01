import type { CaseImportRow } from "../typing/types/case-import-row.type";
import type { CaseImportPreviewItem } from "../typing/types/test-case.type";

export const buildCaseImportRows = (items: readonly CaseImportPreviewItem[]): CaseImportRow[] => {
  return items.map((item) => {
    const isSelectable = item.problem === null;

    return { item, isSelectable, isIncluded: isSelectable && !item.isDuplicate };
  });
};

export const includeAllCaseImportRows = (
  rows: readonly CaseImportRow[],
  isIncluded: boolean,
): CaseImportRow[] => {
  return rows.map((row) => {
    return row.isSelectable ? { ...row, isIncluded } : row;
  });
};

export const toggleCaseImportRow = (
  rows: readonly CaseImportRow[],
  index: number,
  isIncluded: boolean,
): CaseImportRow[] => {
  return rows.map((row) => {
    return row.item.index === index && row.isSelectable ? { ...row, isIncluded } : row;
  });
};

export const readIncludedCaseImportIndexes = (rows: readonly CaseImportRow[]): number[] => {
  return rows
    .filter((row) => row.isIncluded)
    .map((row) => {
      return row.item.index;
    });
};
