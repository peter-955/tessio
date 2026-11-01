import type { ManualCaseResultRequest } from "./manual-run.type";

export interface ManualCaseResultVariables {
  testCaseId: string;
  body: ManualCaseResultRequest;
}
