import type { DataItem } from "./data-item.type";

export interface DataGridRow {
  key: string;
  itemByScopeId: Record<string, DataItem>;
}
