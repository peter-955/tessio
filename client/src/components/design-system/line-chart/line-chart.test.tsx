import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSLineChart } from "./line-chart";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

const formatPercent = (value: number): string => {
  return `${String(value)}%`;
};

describe("DSLineChart", () => {
  it("names the chart and lists every point in a table for screen readers", async () => {
    const { container } = render(
      <DSLineChart
        label="Pass rate over time"
        xKey="day"
        xLabel="Day"
        data={[
          { day: "1 Nov", passRate: 80, flakyRate: 5 },
          { day: "2 Nov", passRate: 90, flakyRate: null },
        ]}
        series={[
          { key: "passRate", label: "Pass rate", color: "series1" },
          { key: "flakyRate", label: "Flaky rate", color: "series2" },
        ]}
        valueFormatter={formatPercent}
      />,
      { wrapper },
    );

    const figure = screen.getByRole("figure", { name: "Pass rate over time" });
    const table = within(figure).getByRole("table", { name: "Pass rate over time" });
    expect(within(table).getByRole("columnheader", { name: "Pass rate" })).toBeInTheDocument();
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(within(rows[1]).getByRole("rowheader", { name: "1 Nov" })).toBeInTheDocument();
    expect(
      within(rows[1])
        .getAllByRole("cell")
        .map((cell) => cell.textContent),
    ).toEqual(["80%", "5%"]);
    expect(
      within(rows[2])
        .getAllByRole("cell")
        .map((cell) => cell.textContent),
    ).toEqual(["90%", "–"]);
    expect(await axe(container)).toHaveNoViolations();
  });
});
