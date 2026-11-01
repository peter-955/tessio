import type { components } from "@/lib/api/openapi.type";
import type { CoverageSegmentKind } from "../enums/coverage-segment-kind.enum";

export type DashboardSummary = components["schemas"]["DashboardResponse"];

export type DashboardSprint = NonNullable<DashboardSummary["sprint"]>;

export type TestStatusCounts = components["schemas"]["TestStatusCountsResponse"];

export type CoverageCounts = components["schemas"]["CoverageCountResponse"];

export type TestStatus = components["schemas"]["TestStatus"];

export type SprintState = components["schemas"]["SprintState"];

export interface CoverageSegment {
  kind: CoverageSegmentKind;
  count: number;
}

export interface TestStatusRow {
  status: TestStatus;
  count: number;
  href: string;
}
