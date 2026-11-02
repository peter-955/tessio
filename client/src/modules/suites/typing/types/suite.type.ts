import type { components } from "@/lib/api/openapi.type";

export type SuiteSummary = components["schemas"]["SuiteSummaryResponse"];

export type SuiteDetail = components["schemas"]["SuiteDetailResponse"];

export type SuiteCase = components["schemas"]["SuiteCaseResponse"];

export type SuiteRunReference = components["schemas"]["SuiteRunReferenceResponse"];

export type SuiteCasesAdded = components["schemas"]["SuiteCasesAddedResponse"];

export type CreateSuiteRequest = components["schemas"]["CreateSuiteRequest"];

export type UpdateSuiteRequest = components["schemas"]["UpdateSuiteRequest"];

export type AddSuiteCasesByFilterRequest = components["schemas"]["AddSuiteCasesByFilterRequest"];

export type SkipReason = components["schemas"]["SkipReason"];

export type SkippedRunCase = components["schemas"]["SkippedRunCaseResponse"];
