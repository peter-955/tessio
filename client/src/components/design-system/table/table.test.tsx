import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSTable } from "./table";

const renderTable = (label?: string): HTMLElement => {
  const { container } = render(
    <DSTable label={label}>
      <thead>
        <tr>
          <th scope="col">Name</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Staging</td>
        </tr>
      </tbody>
    </DSTable>,
  );

  return container;
};

describe("DSTable", () => {
  it("is a focusable named region so a keyboard can scroll it", async () => {
    const user = userEvent.setup();
    const container = renderTable("Environments");

    const region = screen.getByRole("region", { name: "Environments" });
    await user.tab();
    expect(region).toHaveFocus();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("stays focusable without a region role when no label is given", () => {
    const container = renderTable();

    expect(screen.queryByRole("region")).not.toBeInTheDocument();
    expect(container.firstElementChild).toHaveAttribute("tabindex", "0");
  });
});
