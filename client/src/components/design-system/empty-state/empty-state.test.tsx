import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSEmptyState } from "./empty-state";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSEmptyState", () => {
  it("renders the title, description and action without accessibility violations", async () => {
    const { container } = render(
      <DSEmptyState
        title="No test cases yet"
        description="Generate cases from a story to get started."
        action={<button type="button">Generate</button>}
      />,
      { wrapper },
    );

    expect(screen.getByText("No test cases yet")).toBeInTheDocument();
    expect(screen.getByText("Generate cases from a story to get started.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Generate" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders without description and action", () => {
    render(<DSEmptyState title="Nothing here" size="sm" icon="file" />, { wrapper });

    expect(screen.getByText("Nothing here")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
