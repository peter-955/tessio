import type { DataTableErrors } from "@/modules/data-rows/typing/types/data-table-errors.type";

export type TestCaseFormErrorKey = "required" | "tooLong" | "tooMany";

export interface TestCaseFormErrors {
  storyKey?: TestCaseFormErrorKey;
  title?: TestCaseFormErrorKey;
  businessValue?: TestCaseFormErrorKey;
  preconditions?: TestCaseFormErrorKey;
  criterionIds?: TestCaseFormErrorKey;
  steps?: TestCaseFormErrorKey;
  stepActions: Record<string, TestCaseFormErrorKey>;
  dataTable?: DataTableErrors;
}
