import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSTabPanel } from "./tab-panel/tab-panel";
import { DSTabs } from "./tabs";

type TabValue = "cases" | "runs";

interface Props {
  onChange: (value: TabValue) => void;
}

const ControlledTabs = ({ onChange }: Props) => {
  const [value, setValue] = useState<TabValue>("cases");

  return (
    <MantineProvider theme={mantineTheme} env="test">
      <DSTabs<TabValue>
        ariaLabel="Story sections"
        value={value}
        items={[
          { value: "cases", label: "Test cases", count: 3 },
          { value: "runs", label: "Runs", icon: "runs" },
        ]}
        onChange={(nextValue) => {
          onChange(nextValue);
          setValue(nextValue);
        }}
      >
        <DSTabPanel value="cases">Cases panel</DSTabPanel>
        <DSTabPanel value="runs">Runs panel</DSTabPanel>
      </DSTabs>
    </MantineProvider>
  );
};

describe("DSTabs", () => {
  it("calls onChange with the tab value and switches the panel", async () => {
    const handleChange = vi.fn<(value: TabValue) => void>();
    render(<ControlledTabs onChange={handleChange} />);

    expect(screen.getByRole("tablist", { name: "Story sections" })).toBeInTheDocument();
    expect(screen.getByText("Cases panel")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("tab", { name: "Runs" }));

    expect(handleChange).toHaveBeenCalledWith("runs");
    expect(screen.getByText("Runs panel")).toBeInTheDocument();
    expect(screen.queryByText("Cases panel")).not.toBeInTheDocument();
  });

  it("does not render tabs other than the given items", () => {
    render(
      <DSTabs<TabValue>
        ariaLabel="Sections"
        value="cases"
        items={[{ value: "cases", label: "Test cases" }]}
        onChange={vi.fn()}
      >
        <DSTabPanel value="cases">Only panel</DSTabPanel>
      </DSTabs>,
      {
        wrapper: ({ children }: { children: ReactNode }) => {
          return (
            <MantineProvider theme={mantineTheme} env="test">
              {children}
            </MantineProvider>
          );
        },
      },
    );

    expect(screen.getAllByRole("tab")).toHaveLength(1);
  });

  it("moves between tabs with the arrow keys and has no axe violations", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn<(value: TabValue) => void>();
    const { container } = render(<ControlledTabs onChange={handleChange} />);

    await user.tab();
    expect(screen.getByRole("tab", { name: /Test cases/ })).toHaveFocus();
    await user.keyboard("{ArrowRight}");

    expect(screen.getByRole("tab", { name: "Runs" })).toHaveFocus();
    expect(handleChange).toHaveBeenCalledWith("runs");
    expect(await axe(container)).toHaveNoViolations();
  });
});
