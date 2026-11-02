import type { DSChartColor } from "../types/chart.type";

export const DS_CHART_COLORS: Readonly<Record<DSChartColor, string>> = {
  series1: "var(--color-chart-1)",
  series2: "var(--color-chart-2)",
  series3: "var(--color-chart-3)",
  series4: "var(--color-chart-4)",
  series5: "var(--color-chart-5)",
  success: "var(--color-success)",
  danger: "var(--color-danger)",
  warning: "var(--color-warning)",
  muted: "var(--color-text-muted)",
};

export const DS_CHART_GRID_COLOR = "var(--color-border)";

export const DS_CHART_TEXT_COLOR = "var(--color-text-muted)";

export const DS_CHART_DEFAULT_HEIGHT = 260;

export const DS_DONUT_DEFAULT_SIZE = 160;

export const DS_DONUT_THICKNESS = 20;

export const DS_CHART_STROKE_WIDTH = 2;

export const DS_BAR_MAX_WIDTH = 32;
