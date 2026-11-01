import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSTimeline } from "./timeline";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSTimeline", () => {
  it("renders every item with its details", () => {
    render(
      <DSTimeline
        activeIndex={1}
        items={[
          { key: "opened", title: "Failure opened", time: "10:02", icon: "alert", color: "red" },
          { key: "linked", title: "Linked to Jira", description: "PROJ-12" },
          { key: "resolved", title: "Resolved", icon: "check", color: "green" },
        ]}
      />,
      { wrapper },
    );

    expect(screen.getAllByRole("listitem")).toHaveLength(3);
    expect(screen.getByText("Failure opened")).toBeInTheDocument();
    expect(screen.getByText("PROJ-12")).toBeInTheDocument();
    expect(screen.getByText("10:02")).toBeInTheDocument();
  });

  it("has no axe violations", async () => {
    const { container } = render(
      <DSTimeline
        activeIndex={0}
        items={[
          { key: "opened", title: "Failure opened", time: "10:02", icon: "alert", color: "red" },
          { key: "resolved", title: "Resolved", icon: "check", color: "green" },
        ]}
      />,
      { wrapper },
    );

    expect(await axe(container)).toHaveNoViolations();
  });
});
