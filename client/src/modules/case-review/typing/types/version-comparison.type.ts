import type { TestCasePriority } from "@/modules/test-cases/typing/types/test-case.type";
import type { DiffToken } from "@/modules/test-cases/typing/types/version-diff.type";

export type CompareRowKind = "unchanged" | "changed" | "added" | "removed";

export type CompareTextField = "title" | "businessValue" | "preconditions";

export interface CompareTextRow {
  field: CompareTextField;
  kind: "unchanged" | "changed";
  left: DiffToken[];
  right: DiffToken[];
}

export interface ComparePriorityRow {
  kind: "unchanged" | "changed";
  left: TestCasePriority;
  right: TestCasePriority;
}

export interface CompareStepSide {
  order: number;
  action: DiffToken[];
  expected: DiffToken[];
}

export interface CompareStepRow {
  kind: CompareRowKind;
  left: CompareStepSide | null;
  right: CompareStepSide | null;
}

export interface CompareDataTableRow {
  kind: "unchanged" | "changed";
  left: DiffToken[];
  right: DiffToken[];
}

export interface VersionComparison {
  fields: CompareTextRow[];
  priority: ComparePriorityRow;
  dataTable: CompareDataTableRow | null;
  steps: CompareStepRow[];
  changeCount: number;
}
