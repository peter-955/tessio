import type { UpdateSuiteRequest } from "./suite.type";

export interface SuiteUpdateVariables {
  suiteId: string;
  body: UpdateSuiteRequest;
}
