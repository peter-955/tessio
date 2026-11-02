import type { components } from "@/lib/api/openapi.type";

export type InsightTrends = components["schemas"]["TrendsResponse"];

export type TrendPoint = components["schemas"]["TrendPointResponse"];

export type TrendGrouping = components["schemas"]["TrendGrouping"];

export type InsightSprint =
  components["schemas"]["app__modules__insights__models__sprint_reference_response__SprintReferenceResponse"];

export type LabelCoverageReport = components["schemas"]["LabelCoverageReportResponse"];

export type LabelCoverage = components["schemas"]["LabelCoverageResponse"];

export type CaseShareCounts = components["schemas"]["CaseShareCountsResponse"];

export type FailingCase = components["schemas"]["FailingCaseResponse"];

export type FlakyCase = components["schemas"]["FlakyCaseResponse"];

export type TokenUsage = components["schemas"]["TokenUsageResponse"];

export type TokenRun = components["schemas"]["TokenRunResponse"];

export type SprintCoverage = components["schemas"]["SprintCoverageResponse"];

export type InsightCoverageCounts = components["schemas"]["CoverageCountResponse"];
