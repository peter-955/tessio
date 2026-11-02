import type { ReportFormat } from "../types/report.type";

export const REPORT_FORMATS: readonly ReportFormat[] = ["md", "pdf"];

export const DEFAULT_REPORT_FORMAT: ReportFormat = "pdf";

export const REPORT_LINK_POLL_INTERVAL_IN_MILLISECONDS = 5000;

export const REPORT_LINK_MAX_POLL_COUNT = 60;

export const REPORT_LINK_REFRESH_INTERVAL_IN_MILLISECONDS = 240000;

export const NOT_FOUND_STATUS = 404;

export const NEW_TAB_TARGET = "_blank";

export const NEW_TAB_FEATURES = "noopener";
