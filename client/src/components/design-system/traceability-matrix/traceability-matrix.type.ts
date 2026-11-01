export type DSTraceabilityResultStatus = "passed" | "failed" | "blocked" | "skipped" | "not_run";

export type DSTraceabilityCriterionStatus =
  "uncovered" | "not_run" | "passed" | "failed" | "blocked";

export interface DSTraceabilityCase {
  id: string;
  code: string;
  title: string;
  href: string;
  resultStatus: DSTraceabilityResultStatus;
  markers: readonly string[];
}

export interface DSTraceabilityCriterion {
  id: string;
  code: string;
  text: string;
  status: DSTraceabilityCriterionStatus;
  removedLabel: string | null;
  linkedCaseIds: readonly string[];
}

export interface DSTraceabilityMatrixLabels {
  caption: string;
  criterion: string;
  status: string;
  notLinked: string;
  resultStatuses: Record<DSTraceabilityResultStatus, string>;
  criterionStatuses: Record<DSTraceabilityCriterionStatus, string>;
}
