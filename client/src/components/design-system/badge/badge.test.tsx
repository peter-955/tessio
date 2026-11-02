import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSBadge } from "./badge";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSBadge", () => {
  it.each([
    ["red", "var(--color-red-text)"],
    ["green", "var(--color-green-text)"],
    ["yellow", "var(--color-yellow-text)"],
    ["orange", "var(--color-orange-text)"],
    ["teal", "var(--color-teal-text)"],
    ["blue", "var(--color-blue-text)"],
    ["violet", "var(--color-violet-text)"],
  ] as const)("uses the contrast-safe text token for %s", (color, token) => {
    render(<DSBadge color={color}>Failed</DSBadge>, { wrapper });

    expect(screen.getByText("Failed").closest(".mantine-Badge-root")).toHaveAttribute(
      "style",
      expect.stringContaining(`color: ${token}`),
    );
  });

  it("keeps the Mantine colour for gray, tessio and dot badges", async () => {
    const { container } = render(
      <>
        <DSBadge>Draft</DSBadge>
        <DSBadge color="tessio">Ready</DSBadge>
        <DSBadge color="red" hasDot>
          Open
        </DSBadge>
      </>,
      { wrapper },
    );

    for (const label of ["Draft", "Ready", "Open"]) {
      expect(screen.getByText(label).closest(".mantine-Badge-root")).not.toHaveAttribute(
        "style",
        expect.stringContaining("--color-"),
      );
    }
    expect(await axe(container)).toHaveNoViolations();
  });
});
