import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSDonutChart } from "./donut-chart";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

const formatRuns = (value: number): string => {
  return `${String(value)} runs`;
};

describe("DSDonutChart", () => {
  it("names the chart and lists every segment in a table for screen readers", async () => {
    const { container } = render(
      <DSDonutChart
        label="Runs by executor"
        segmentLabel="Executor"
        valueLabel="Runs"
        centerLabel="10 runs"
        segments={[
          { key: "claude", label: "Claude", value: 7, color: "series1" },
          { key: "manual", label: "Manual", value: 3, color: "series2" },
        ]}
        valueFormatter={formatRuns}
      />,
      { wrapper },
    );

    const figure = screen.getByRole("figure", { name: "Runs by executor" });
    const table = within(figure).getByRole("table", { name: "Runs by executor" });
    const claudeRow = within(table).getByRole("rowheader", { name: "Claude" }).closest("tr");
    expect(claudeRow).not.toBeNull();
    expect(within(claudeRow as HTMLElement).getByRole("cell")).toHaveTextContent("7 runs");
    expect(within(table).getByRole("rowheader", { name: "Manual" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
