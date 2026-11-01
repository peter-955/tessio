import type { DataItemKind } from "./data-item.type";
import type { ImportAction } from "./import.type";

export interface ImportRow {
  key: string;
  kind: DataItemKind;
  suggestedKind: DataItemKind;
  value: string | null;
  action: ImportAction;
  isIncluded: boolean;
}
