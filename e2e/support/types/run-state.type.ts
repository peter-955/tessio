export interface RunState {
  firstRunId: string;
  rerunId: string;
  failureId: string;
  caseCode: string;
  suiteId: string;
  suiteRunId: string;
  qcRecoveryCodes: string[];
}
