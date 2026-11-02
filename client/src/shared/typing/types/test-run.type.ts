import type { components } from "@/lib/api/openapi.type";

export type RunStatus = components["schemas"]["RunStatus"];

export type ResultStatus = components["schemas"]["ResultStatus"];

export type RunExecutor = components["schemas"]["RunExecutor"];

export type RunAbortReason = components["schemas"]["RunAbortReason"];

export type RunSummary = components["schemas"]["RunSummaryResponse"];

export type RunDetail = components["schemas"]["RunDetailResponse"];

export type RunCase = components["schemas"]["RunCaseResponse"];

export type StepResult = components["schemas"]["StepResultResponse"];

export type RunReport = components["schemas"]["RunReportResponse"];

export type RunCounts = components["schemas"]["RunCountsResponse"];

export type TestOutcome = RunStatus | ResultStatus | "pending" | "not_reported";

export type SuspectedCause = components["schemas"]["SuspectedCause"];

export type StepDiagnosis = components["schemas"]["StepDiagnosisResponse"];
