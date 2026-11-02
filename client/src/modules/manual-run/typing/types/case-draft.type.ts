import type { SuspectedCause } from "@/shared/typing/types/test-run.type";
import type { ResultStatus } from "./manual-run.type";
import type { StepDraft } from "./step-draft.type";

export interface CaseDraft {
  steps: Record<number, StepDraft>;
  statusOverride: ResultStatus | null;
  suspectedCause: SuspectedCause | null;
  causeReason: string;
}
