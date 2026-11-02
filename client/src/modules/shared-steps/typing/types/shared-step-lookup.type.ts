import type { SharedStep } from "./shared-step.type";

export interface SharedStepLookup {
  sharedStep: SharedStep | null;
  isPending: boolean;
  isError: boolean;
}
