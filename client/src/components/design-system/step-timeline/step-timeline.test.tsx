import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSStepTimeline } from "./step-timeline";
import type { DSStepTimelineLabels, DSStepTimelineStep } from "./step-timeline.type";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

const LABELS: DSStepTimelineLabels = {
  step: (order) => `Step ${String(order)}`,
  expected: "Expected",
  actualResult: "Actual result",
  error: "Error",
};

const STEPS: DSStepTimelineStep[] = [
  {
    key: "1",
    order: 1,
    action: "Open the cart",
    expected: "The cart is shown",
    status: "passed",
    statusLabel: "Passed",
    actualResult: "The cart was shown",
    error: null,
    media: <span>Screenshot one</span>,
  },
  {
    key: "2",
    order: 2,
    action: "Pay with a card",
    expected: null,
    status: "failed",
    statusLabel: "Failed",
    actualResult: "Nothing happened",
    error: "TimeoutError: button not clickable",
  },
  {
    key: "3",
    order: 3,
    action: "See the receipt",
    expected: "A receipt",
    status: "not_reported",
    statusLabel: "Not reported",
    actualResult: null,
    error: null,
  },
];

describe("DSStepTimeline", () => {
  it("renders every step with its status label, details and media", async () => {
    const { container } = render(
      <DSStepTimeline steps={STEPS} labels={LABELS} ariaLabel="Steps of TC-1" />,
      { wrapper },
    );

    const list = screen.getByRole("list", { name: "Steps of TC-1" });
    const items = within(list).getAllByRole("listitem");
    expect(items).toHaveLength(3);
    expect(within(items[0]).getByText("Step 1")).toBeInTheDocument();
    expect(within(items[0]).getByText("Open the cart")).toBeInTheDocument();
    expect(within(items[0]).getByText("Passed")).toBeInTheDocument();
    expect(within(items[0]).getByText("The cart is shown")).toBeInTheDocument();
    expect(within(items[0]).getByText("Screenshot one")).toBeInTheDocument();
    expect(within(items[1]).getByText("Failed")).toBeInTheDocument();
    expect(within(items[1]).getByText("TimeoutError: button not clickable")).toBeInTheDocument();
    expect(within(items[1]).queryByText("Expected")).not.toBeInTheDocument();
    expect(within(items[2]).getByText("Not reported")).toBeInTheDocument();
    expect(within(items[2]).queryByText("Actual result")).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("numbers steps that have no status and links each one to the next", async () => {
    const { container } = render(
      <DSStepTimeline
        steps={[
          { key: "1", order: 1, action: "Open the cart", expected: "The cart is shown" },
          { key: "2", order: 2, action: "Pay with a card", expected: null },
        ]}
        labels={{ step: LABELS.step, expected: LABELS.expected }}
        ariaLabel="Steps of TC-2"
      />,
      { wrapper },
    );

    const items = within(screen.getByRole("list", { name: "Steps of TC-2" })).getAllByRole(
      "listitem",
    );
    expect(items).toHaveLength(2);
    expect(within(items[0] as HTMLElement).getByText("1")).toBeInTheDocument();
    expect(within(items[0] as HTMLElement).getByText("Step 1")).toBeInTheDocument();
    expect(within(items[0] as HTMLElement).getByText("The cart is shown")).toBeInTheDocument();
    expect(within(items[1] as HTMLElement).getByText("2")).toBeInTheDocument();
    expect(within(items[1] as HTMLElement).queryByText("Expected")).not.toBeInTheDocument();
    expect(within(items[1] as HTMLElement).queryByText("Passed")).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows a header action and custom details in a step", () => {
    render(
      <DSStepTimeline
        steps={[
          {
            key: "a",
            order: 1,
            action: null,
            expected: null,
            titleId: "step-a",
            headerAction: <button type="button">Step actions</button>,
            details: (
              <div role="group" aria-labelledby="step-a">
                Fields
              </div>
            ),
          },
        ]}
        labels={{ step: LABELS.step, expected: LABELS.expected }}
      />,
      { wrapper },
    );

    expect(screen.getByRole("button", { name: "Step actions" })).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Step 1" })).toHaveTextContent("Fields");
  });
});
