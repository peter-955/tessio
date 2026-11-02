import type { components } from "@/lib/api/openapi.type";

export type PlanSummary = components["schemas"]["PlanSummaryResponse"];

export type PlanDetail = components["schemas"]["PlanDetailResponse"];

export type PlanItem = components["schemas"]["PlanItemResponse"];

export type PlanCase = components["schemas"]["PlanCaseResponse"];

export type PlanFailure = components["schemas"]["PlanFailureResponse"];

export type PlanGap = components["schemas"]["PlanGapResponse"];

export type PlanProgressCounts = components["schemas"]["PlanProgressCountsResponse"];

export type PlanStatus = components["schemas"]["PlanStatus"];

export type PlanItemKind = components["schemas"]["PlanItemKind"];

export type PlanResultStatus = components["schemas"]["ResultStatus"];

export type PlanSuiteSummary = components["schemas"]["SuiteSummaryResponse"];

export type CreatePlanRequest = components["schemas"]["CreatePlanRequest"];

export type UpdatePlanRequest = components["schemas"]["UpdatePlanRequest"];

export type PlanItemRequest = components["schemas"]["PlanItemRequest"];

export type SetPlanItemsRequest = components["schemas"]["SetPlanItemsRequest"];

export type PlanGapSeverity = components["schemas"]["GapSeverity"];
