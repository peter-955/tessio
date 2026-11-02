import type { components } from "@/lib/api/openapi.type";

export type ManualRun = components["schemas"]["RunDetailResponse"];

export type ManualRunCase = components["schemas"]["RunCaseResponse"];

export type ManualRunStep = components["schemas"]["StepResultResponse"];

export type ResultStatus = components["schemas"]["ResultStatus"];

export type RunExecutor = components["schemas"]["RunExecutor"];

export type RunStatus = components["schemas"]["RunStatus"];

export type CreateManualRunRequest = components["schemas"]["ManualRunCreateRequest"];

export type ManualCaseResultRequest = components["schemas"]["ManualCaseResultRequest"];

export type ManualStepResultInput = components["schemas"]["ManualStepResultInput"];

export type ManualCaseResult = components["schemas"]["ManualCaseResultResponse"];

export type ManualRunCreated = components["schemas"]["ManualRunResponse"];

export type ManualRerunRequest = components["schemas"]["ManualRerunRequest"];

export type ManualFinishRequest = components["schemas"]["ManualFinishRequest"];

export type RunStory = components["schemas"]["StorySummaryResponse"];

export type ReadyTestCase = components["schemas"]["TestCaseSummaryResponse"];

export type RunEnvironment = components["schemas"]["EnvironmentResponse"];

export type ResolveDataRequest = components["schemas"]["ResolveDataRequest"];

export type ResolvedData = components["schemas"]["ResolvedDataResponse"];
