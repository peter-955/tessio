import type { DSStepEditorStep } from "@/components/design-system";
import type { DataTableValues } from "@/modules/data-rows/typing/types/data-table.type";
import type { TestCasePriority } from "./test-case.type";

export interface TestCaseFormValues {
  storyKey: string | null;
  title: string;
  priority: TestCasePriority;
  businessValue: string;
  preconditions: string;
  criterionIds: string[];
  steps: DSStepEditorStep[];
  dataTable: DataTableValues;
}
