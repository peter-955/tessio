import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSProgress } from "./progress";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSProgress", () => {
  it("renders one named progress bar per section with a value", async () => {
    const { container } = render(
      <DSProgress
        label="Plan progress"
        sections={[
          { key: "passed", value: 50, color: "green", label: "Passed: 2" },
          { key: "failed", value: 25, color: "red", label: "Failed: 1" },
          { key: "blocked", value: 0, color: "yellow", label: "Blocked: 0" },
        ]}
      />,
      { wrapper },
    );

    expect(screen.getByRole("group", { name: "Plan progress" })).toBeInTheDocument();
    const bars = screen.getAllByRole("progressbar");
    expect(bars).toHaveLength(2);
    expect(screen.getByRole("progressbar", { name: "Passed: 2" })).toHaveAttribute(
      "aria-valuenow",
      "50",
    );
    expect(screen.queryByRole("progressbar", { name: "Blocked: 0" })).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});
