import type { CaseImportPreviewItem } from "./test-case.type";

export interface CaseImportRow {
  item: CaseImportPreviewItem;
  isSelectable: boolean;
  isIncluded: boolean;
}
