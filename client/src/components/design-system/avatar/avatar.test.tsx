import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSAvatar } from "./avatar";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSAvatar", () => {
  it("shows the initials when there is no image", () => {
    render(<DSAvatar name="Jane Doe" />, { wrapper });

    expect(screen.getByText("JD")).toBeInTheDocument();
  });

  it("renders the image with the name as alt text", () => {
    render(<DSAvatar name="Jane Doe" src="https://example.test/jane.png" />, { wrapper });

    expect(screen.getByRole("img", { name: "Jane Doe" })).toHaveAttribute(
      "src",
      "https://example.test/jane.png",
    );
  });

  it("has no axe violations with or without an image", async () => {
    const { container } = render(
      <>
        <DSAvatar name="Jane Doe" />
        <DSAvatar name="Lan Nguyen" src="https://example.test/lan.png" />
      </>,
      { wrapper },
    );

    expect(await axe(container)).toHaveNoViolations();
  });
});
