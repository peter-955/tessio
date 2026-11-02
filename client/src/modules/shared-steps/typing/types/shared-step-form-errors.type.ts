export type SharedStepFormErrorKey = "required" | "tooLong" | "tooMany" | "invalidKey";

export interface SharedStepFormErrors {
  key?: SharedStepFormErrorKey;
  title?: SharedStepFormErrorKey;
  steps?: SharedStepFormErrorKey;
  stepActions: Record<string, SharedStepFormErrorKey>;
}
