import type { TestCasePriority } from "@/modules/test-cases/typing/types/test-case.type";

export interface SuiteFilterValues {
  labels: string[];
  priorities: TestCasePriority[];
  storyKey: string | null;
  sprintId: string | null;
}
