import { BarChart } from "@mantine/charts";
import type { FC } from "react";
import { ChartDataTable } from "../chart-data-table/chart-data-table";
import styles from "../chart-data-table/chart-data-table.module.scss";
import {
  DS_BAR_MAX_WIDTH,
  DS_CHART_COLORS,
  DS_CHART_DEFAULT_HEIGHT,
  DS_CHART_GRID_COLOR,
  DS_CHART_TEXT_COLOR,
} from "../typing/constants/chart.constant";
import type {
  DSChartDatum,
  DSChartSeries,
  DSChartValueFormatter,
} from "../typing/types/chart.type";

interface Props {
  label: string;
  data: DSChartDatum[];
  xKey: string;
  xLabel: string;
  series: DSChartSeries[];
  height?: number;
  isHorizontal?: boolean;
  isStacked?: boolean;
  unit?: string;
  valueFormatter?: DSChartValueFormatter;
}

export const DSBarChart: FC<Props> = ({
  label,
  data,
  xKey,
  xLabel,
  series,
  height = DS_CHART_DEFAULT_HEIGHT,
  isHorizontal = false,
  isStacked = false,
  unit,
  valueFormatter,
}) => {
  return (
    <figure aria-label={label} className={styles.figure}>
      <BarChart
        h={height}
        data={data}
        dataKey={xKey}
        series={series.map((item) => {
          return { name: item.key, label: item.label, color: DS_CHART_COLORS[item.color] };
        })}
        type={isStacked ? "stacked" : "default"}
        orientation={isHorizontal ? "vertical" : "horizontal"}
        maxBarWidth={DS_BAR_MAX_WIDTH}
        withLegend={series.length > 1}
        gridColor={DS_CHART_GRID_COLOR}
        textColor={DS_CHART_TEXT_COLOR}
        unit={unit}
        valueFormatter={valueFormatter}
        accessibilityLayer={false}
        aria-hidden
      />
      <ChartDataTable
        caption={label}
        rowHeader={{ key: xKey, label: xLabel }}
        columns={series}
        rows={data}
        valueFormatter={valueFormatter}
      />
    </figure>
  );
};
