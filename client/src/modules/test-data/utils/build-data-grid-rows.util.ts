import { PROJECT_SCOPE_ID } from "../typing/constants/test-data.constant";
import type { DataGridRow } from "../typing/types/data-grid-row.type";
import type { DataItem } from "../typing/types/data-item.type";

export const resolveDataItemScopeId = (item: Pick<DataItem, "environmentId">): string => {
  return item.environmentId ?? PROJECT_SCOPE_ID;
};

export const buildDataGridRows = (items: readonly DataItem[]): DataGridRow[] => {
  const rowByKey = new Map<string, DataGridRow>();

  items.forEach((item) => {
    const row = rowByKey.get(item.key) ?? { key: item.key, itemByScopeId: {} };
    row.itemByScopeId[resolveDataItemScopeId(item)] = item;
    rowByKey.set(item.key, row);
  });

  return [...rowByKey.values()];
};

export const findRowKind = (row: DataGridRow): DataItem["kind"] => {
  const projectItem = row.itemByScopeId[PROJECT_SCOPE_ID];
  const firstItem = projectItem ?? Object.values(row.itemByScopeId)[0];

  return firstItem?.kind ?? "variable";
};

export const findRowDescription = (row: DataGridRow): string | null => {
  const projectItem = row.itemByScopeId[PROJECT_SCOPE_ID];
  const items = projectItem === undefined ? Object.values(row.itemByScopeId) : [projectItem];
  const describedItem = items.find((item) => {
    return item.description !== null && item.description !== "";
  });

  return describedItem?.description ?? null;
};

export const filterDataGridRows = (rows: readonly DataGridRow[], search: string): DataGridRow[] => {
  const normalizedSearch = search.trim().toLowerCase();
  if (normalizedSearch === "") {
    return [...rows];
  }

  return rows.filter((row) => {
    return row.key.toLowerCase().includes(normalizedSearch);
  });
};
