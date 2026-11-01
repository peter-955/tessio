import type { components } from "@/lib/api/openapi.type";

export type MyWork = components["schemas"]["MyWorkResponse"];

export type MyWorkSection = components["schemas"]["MyWorkSection"];

export type UncoveredCriterionItem = components["schemas"]["UncoveredCriterionItemResponse"];

export type DraftCaseItem = components["schemas"]["DraftCaseItemResponse"];

export type FailureToFixItem = components["schemas"]["FailureToFixItemResponse"];

export type GapToAnswerItem = components["schemas"]["GapToAnswerItemResponse"];

export type TestCaseStatus = components["schemas"]["TestCaseStatus"];

export type FailureStatus = components["schemas"]["FailureStatus"];

export type GapSeverity = components["schemas"]["GapSeverity"];
