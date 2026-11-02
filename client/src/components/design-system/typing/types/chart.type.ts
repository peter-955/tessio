export type DSChartColor =
  | "series1"
  | "series2"
  | "series3"
  | "series4"
  | "series5"
  | "success"
  | "danger"
  | "warning"
  | "muted";

export interface DSChartSeries {
  key: string;
  label: string;
  color: DSChartColor;
}

export type DSChartDatum = Record<string, string | number | null>;

export interface DSDonutSegment {
  key: string;
  label: string;
  value: number;
  color: DSChartColor;
}

export type DSChartValueFormatter = (value: number) => string;
