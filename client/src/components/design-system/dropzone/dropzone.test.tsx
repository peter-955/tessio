import { mantineTheme } from "@/lib/mantine/mantine-theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import { DSDropzone } from "./dropzone";

const TITLE = "Drop a file here or browse";
const DESCRIPTION = "PNG or JPEG, up to 5 MB";

const wrapper = ({ children }: { children: ReactNode }) => {
  return (
    <MantineProvider theme={mantineTheme} env="test">
      {children}
    </MantineProvider>
  );
};

const renderDropzone = () => {
  const handleDrop = vi.fn<(files: File[]) => void>();
  const result = render(
    <DSDropzone title={TITLE} description={DESCRIPTION} onDrop={handleDrop} />,
    { wrapper },
  );
  const input = result.container.querySelector<HTMLInputElement>('input[type="file"]');
  if (input === null) {
    throw new Error("The dropzone has no file input");
  }
  return { ...result, input };
};

describe("DSDropzone", () => {
  it("is a button named by its title and described by its description", () => {
    const { input } = renderDropzone();

    const dropzone = screen.getByRole("button", { name: TITLE });
    expect(dropzone).toHaveAccessibleDescription(DESCRIPTION);
    expect(dropzone).not.toHaveAttribute("aria-disabled");
    expect(input).toHaveAttribute("aria-label", TITLE);
  });

  it.each(["{Enter}", " "])("opens the file picker on %s after Tab", async (key) => {
    const user = userEvent.setup();
    const { input } = renderDropzone();
    const handleInputClick = vi.fn<() => void>();
    input.addEventListener("click", handleInputClick);

    await user.tab();
    expect(screen.getByRole("button", { name: TITLE })).toHaveFocus();
    await user.keyboard(key);

    expect(handleInputClick).toHaveBeenCalled();
  });

  it("has no axe violations", async () => {
    const { container } = renderDropzone();

    expect(await axe(container)).toHaveNoViolations();
  });
});
