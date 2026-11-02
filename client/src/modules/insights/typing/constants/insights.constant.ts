import type { DSChartColor } from "@/components/design-system";
import type { TrendGrouping } from "../types/insights.type";

export const DEFAULT_RANGE_DAYS = 30;

export const MAX_RANGE_DAYS = 366;

export const MILLISECONDS_PER_DAY = 86400000;

export const ISO_DAY_LENGTH = 10;

export const CASE_LIST_LIMIT = 10;

export const TOKEN_CHART_RUN_COUNT = 30;

export const TOKEN_TABLE_RUN_COUNT = 10;

export const PERCENT_SCALE = 100;

export const SECONDS_PER_MINUTE = 60;

export const SECONDS_PER_HOUR = 3600;

export const SECONDS_PER_DAY = 86400;

export const CHART_DECIMALS = 1;

export const LOADING_LINE_COUNT = 5;

export const TREND_GROUPINGS: readonly TrendGrouping[] = ["day", "sprint"];

export const KNOWN_EXECUTORS = ["claude", "manual", "script", "ci"] as const;

export const EXECUTOR_COLORS: Readonly<Partial<Record<string, DSChartColor>>> = {
  claude: "series1",
  manual: "series2",
  script: "series3",
  ci: "series4",
};

export const OTHER_EXECUTOR_COLOR: DSChartColor = "series5";

export const CATEGORY_KEY = "category";
