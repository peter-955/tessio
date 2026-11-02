import type { DataItemKind } from "./data-item.type";

export interface DataItemFormValues {
  key: string;
  kind: DataItemKind;
  scopeId: string;
  value: string;
  description: string;
}
