import { DonutChart } from "@mantine/charts";
import type { FC } from "react";
import { ChartDataTable } from "../chart-data-table/chart-data-table";
import styles from "../chart-data-table/chart-data-table.module.scss";
import {
  DS_CHART_COLORS,
  DS_DONUT_DEFAULT_SIZE,
  DS_DONUT_THICKNESS,
} from "../typing/constants/chart.constant";
import type { DSChartValueFormatter, DSDonutSegment } from "../typing/types/chart.type";

const SEGMENT_KEY = "segment";

const VALUE_KEY = "value";

interface Props {
  label: string;
  segmentLabel: string;
  valueLabel: string;
  segments: DSDonutSegment[];
  centerLabel?: string;
  size?: number;
  valueFormatter?: DSChartValueFormatter;
}

export const DSDonutChart: FC<Props> = ({
  label,
  segmentLabel,
  valueLabel,
  segments,
  centerLabel,
  size = DS_DONUT_DEFAULT_SIZE,
  valueFormatter,
}) => {
  return (
    <figure aria-label={label} className={styles.figure}>
      <DonutChart
        data={segments.map((segment) => {
          return {
            name: segment.label,
            value: segment.value,
            color: DS_CHART_COLORS[segment.color],
          };
        })}
        size={size}
        thickness={DS_DONUT_THICKNESS}
        strokeColor="var(--color-surface)"
        chartLabel={centerLabel}
        withLegend={segments.length > 1}
        valueFormatter={valueFormatter}
        aria-hidden
      />
      <ChartDataTable
        caption={label}
        rowHeader={{ key: SEGMENT_KEY, label: segmentLabel }}
        columns={[{ key: VALUE_KEY, label: valueLabel }]}
        rows={segments.map((segment) => {
          return { [SEGMENT_KEY]: segment.label, [VALUE_KEY]: segment.value };
        })}
        valueFormatter={valueFormatter}
      />
    </figure>
  );
};
