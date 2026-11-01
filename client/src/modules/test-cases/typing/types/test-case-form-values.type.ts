import type { DSStepEditorStep } from "@/components/design-system";
import type { TestCasePriority } from "./test-case.type";

export interface TestCaseFormValues {
  storyKey: string | null;
  title: string;
  priority: TestCasePriority;
  businessValue: string;
  preconditions: string;
  criterionIds: string[];
  steps: DSStepEditorStep[];
}
