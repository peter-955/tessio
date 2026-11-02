import { VisuallyHidden } from "@mantine/core";
import type { FC } from "react";
import type { DSChartValueFormatter } from "../typing/types/chart.type";

interface Column {
  key: string;
  label: string;
}

interface Props {
  caption: string;
  rowHeader: Column;
  columns: Column[];
  rows: Record<string, string | number | null>[];
  valueFormatter?: DSChartValueFormatter;
}

const formatCell = (
  value: string | number | null | undefined,
  valueFormatter: DSChartValueFormatter | undefined,
): string => {
  if (value === null || value === undefined) {
    return "–";
  }
  if (typeof value === "number" && valueFormatter !== undefined) {
    return valueFormatter(value);
  }

  return String(value);
};

export const ChartDataTable: FC<Props> = ({
  caption,
  rowHeader,
  columns,
  rows,
  valueFormatter,
}) => {
  return (
    <VisuallyHidden>
      <table>
        <caption>{caption}</caption>
        <thead>
          <tr>
            <th scope="col">{rowHeader.label}</th>
            {columns.map((column) => {
              return (
                <th key={column.key} scope="col">
                  {column.label}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => {
            return (
              <tr key={`${String(row[rowHeader.key])}-${String(index)}`}>
                <th scope="row">{formatCell(row[rowHeader.key], undefined)}</th>
                {columns.map((column) => {
                  return <td key={column.key}>{formatCell(row[column.key], valueFormatter)}</td>;
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </VisuallyHidden>
  );
};
