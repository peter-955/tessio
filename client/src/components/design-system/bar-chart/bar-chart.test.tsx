import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSBarChart } from "./bar-chart";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSBarChart", () => {
  it("names the chart and lists every bar in a table for screen readers", async () => {
    const { container } = render(
      <DSBarChart
        label="Coverage by label"
        xKey="label"
        xLabel="Label"
        data={[
          { label: "checkout", cases: 12, ready: 9 },
          { label: "login", cases: 4, ready: 4 },
        ]}
        series={[
          { key: "cases", label: "Cases", color: "series1" },
          { key: "ready", label: "Ready", color: "success" },
        ]}
        isHorizontal
      />,
      { wrapper },
    );

    const figure = screen.getByRole("figure", { name: "Coverage by label" });
    const table = within(figure).getByRole("table", { name: "Coverage by label" });
    expect(
      within(table)
        .getAllByRole("columnheader")
        .map((header) => header.textContent),
    ).toEqual(["Label", "Cases", "Ready"]);
    const checkoutRow = within(table).getByRole("rowheader", { name: "checkout" }).closest("tr");
    expect(checkoutRow).not.toBeNull();
    expect(
      within(checkoutRow as HTMLElement)
        .getAllByRole("cell")
        .map((cell) => cell.textContent),
    ).toEqual(["12", "9"]);
    expect(await axe(container)).toHaveNoViolations();
  });
});
