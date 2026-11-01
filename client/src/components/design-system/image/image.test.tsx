import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSImage } from "./image";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

describe("DSImage", () => {
  it("renders the image with its alt text without accessibility violations", async () => {
    const { container } = render(
      <DSImage
        src="https://files.example.test/shot.png"
        alt="Step 2 screenshot"
        fallbackLabel="Image unavailable"
      />,
      { wrapper },
    );

    expect(screen.getByRole("img", { name: "Step 2 screenshot" })).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the fallback label after a load error", async () => {
    const { container } = render(
      <DSImage
        src="https://files.example.test/expired.png"
        alt="Step 2 screenshot"
        fallbackLabel="Image unavailable"
      />,
      { wrapper },
    );

    fireEvent.error(screen.getByRole("img", { name: "Step 2 screenshot" }));

    expect(screen.getByText("Image unavailable")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the fallback label when there is no source", () => {
    render(<DSImage src={null} alt="Step 2 screenshot" fallbackLabel="No screenshot" />, {
      wrapper,
    });

    expect(screen.getByText("No screenshot")).toBeInTheDocument();
  });

  it("opens a zoomed view from the image button", async () => {
    const { container } = render(
      <DSImage
        src="https://files.example.test/shot.png"
        alt="Step 2 screenshot"
        fallbackLabel="Image unavailable"
        isZoomable
        closeLabel="Close preview"
      />,
      { wrapper },
    );

    expect(await axe(container)).toHaveNoViolations();
    await userEvent.click(screen.getByRole("button", { name: "Step 2 screenshot" }));
    expect(screen.getByRole("dialog", { name: "Step 2 screenshot" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Close preview" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
