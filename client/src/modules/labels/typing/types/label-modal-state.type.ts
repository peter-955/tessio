import type { Label } from "./label.type";

export type LabelModalState =
  | { mode: "closed" }
  | { mode: "create" }
  | { mode: "edit"; label: Label }
  | { mode: "delete"; label: Label };
