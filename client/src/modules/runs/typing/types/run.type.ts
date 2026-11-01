import type { components } from "@/lib/api/openapi.type";
import type { ResultStatus, RunStatus } from "@/shared/typing/types/test-run.type";

export type CriterionStatus = components["schemas"]["CriterionStatus"];

export type CriterionImpact = components["schemas"]["CriterionImpactResponse"];

export type FailedCaseReport = components["schemas"]["FailedCaseReportResponse"];

export type MissingScreenshot = components["schemas"]["MissingScreenshotResponse"];

export type StoredFileStatus = components["schemas"]["StoredFileStatus"];

export type FileLink = components["schemas"]["DownloadLinkResponse"];

export interface RunFilters {
  status: RunStatus | null;
  storyKey: string | null;
}

export interface RunListQuery {
  storyKey?: string;
  status?: RunStatus;
  limit: number;
}

export type RunSearchParams = Record<string, string | string[] | undefined>;

export type ScreenshotState = "none" | "uploading" | "missing" | "uploaded";

export type RunCountKey = "passed" | "failed" | "blocked" | "skipped" | "notReported";

export interface RunCountEntry {
  key: RunCountKey;
  count: number;
}

export type ResultOutcome = ResultStatus | "pending" | "not_reported";
