import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSSkeleton } from "./skeleton";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSSkeleton", () => {
  it("renders a hidden placeholder", () => {
    const { container } = render(<DSSkeleton height={40} />, { wrapper });

    expect(container.querySelector("[aria-hidden]")).toBeInTheDocument();
  });

  it("renders the requested number of lines", () => {
    const { container } = render(<DSSkeleton lineCount={3} />, { wrapper });

    const root = container.querySelector("[aria-hidden]");
    expect(root).toBeInTheDocument();
    expect(root?.querySelectorAll(".mantine-Skeleton-root")).toHaveLength(3);
  });

  it("has no axe violations", async () => {
    const { container } = render(<DSSkeleton lineCount={2} />, { wrapper });

    expect(await axe(container)).toHaveNoViolations();
  });
});
