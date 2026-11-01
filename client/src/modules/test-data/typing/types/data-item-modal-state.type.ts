import type { DataItem, DataItemKind } from "./data-item.type";

export interface DataItemCreatePreset {
  key: string;
  kind: DataItemKind;
  scopeId: string;
}

export type DataItemModalState =
  { mode: "create"; preset: DataItemCreatePreset | null } | { mode: "edit"; item: DataItem };
