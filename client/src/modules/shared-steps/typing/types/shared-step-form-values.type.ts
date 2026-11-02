import type { DSStepEditorStep } from "@/components/design-system";

export interface SharedStepFormValues {
  key: string;
  title: string;
  steps: DSStepEditorStep[];
}
