import type { components } from "@/lib/api/openapi.type";

export type Failure = components["schemas"]["FailureResponse"];

export type FailureDetail = components["schemas"]["FailureDetailResponse"];

export type FailureEvent = components["schemas"]["FailureEventResponse"];

export type FailureResult = components["schemas"]["FailureResultResponse"];

export type FailedStep = components["schemas"]["FailedStepResponse"];

export type FailureStatus = components["schemas"]["FailureStatus"];

export type FailureEventKind = components["schemas"]["FailureEventKind"];

export type ResultStatus = components["schemas"]["ResultStatus"];

export type RunExecutor = components["schemas"]["RunExecutor"];

export type FailureRun = components["schemas"]["RunDetailResponse"];

export type RunStepResult = components["schemas"]["StepResultResponse"];

export type DownloadLink = components["schemas"]["DownloadLinkResponse"];
