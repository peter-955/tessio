import englishDataRows from "@/lib/i18n/locales/en/dataRows.json";
import { renderWithProviders } from "@/modules/auth/test/utils/render-with-providers.util";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { axe } from "vitest-axe";
import type { DataTableValues } from "../../typing/types/data-table.type";
import {
  buildDataRows,
  createEmptyDataTable,
  validateDataTable,
} from "../../utils/data-table.util";
import { DataTableEditor } from "./data-table-editor";

vi.mock("next/navigation", () => {
  return {
    useRouter: () => {
      return { push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() };
    },
  };
});

const { editor } = englishDataRows;

const onTableChange = vi.fn<(table: DataTableValues) => void>();

const Harness: FC<{ isValidated?: boolean }> = ({ isValidated = false }) => {
  const [table, setTable] = useState(createEmptyDataTable());

  return (
    <DataTableEditor
      value={table}
      onChange={(nextTable) => {
        setTable(nextTable);
        onTableChange(nextTable);
      }}
      errors={isValidated ? validateDataTable(table) : null}
      isDisabled={false}
    />
  );
};

describe("DataTableEditor", () => {
  it("adds parameters and rows and edits each value", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(<Harness />);

    expect(screen.getByText(editor.noParameters)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: editor.addRow })).toBeDisabled();

    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    await user.type(screen.getByRole("textbox", { name: "Parameter 1 name" }), "email");
    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    await user.type(screen.getByRole("textbox", { name: "Parameter 2 name" }), "role");
    await user.click(screen.getByRole("button", { name: editor.addRow }));
    await user.click(screen.getByRole("button", { name: editor.addRow }));
    await user.type(screen.getByRole("textbox", { name: "Row 1, email" }), "ann@shop.test");
    await user.type(screen.getByRole("textbox", { name: "Row 1, role" }), "admin");
    await user.type(screen.getByRole("textbox", { name: "Row 2, role" }), "qc");

    const table = screen.getByRole("table", { name: editor.tableLabel });
    expect(within(table).getAllByRole("row")).toHaveLength(3);
    const lastTable = onTableChange.mock.lastCall?.[0];
    expect(lastTable === undefined ? null : buildDataRows(lastTable)).toEqual([
      { email: "ann@shop.test", role: "admin" },
      { email: "", role: "qc" },
    ]);

    await user.click(screen.getByRole("button", { name: "Remove row 1" }));
    expect(screen.queryByRole("textbox", { name: "Row 2, role" })).not.toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Row 1, role" })).toHaveValue("qc");

    await user.click(screen.getByRole("button", { name: "Remove parameter role" }));
    expect(screen.queryByRole("textbox", { name: "Row 1, role" })).not.toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("shows the name errors next to the parameter", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness isValidated />);

    await user.click(screen.getByRole("button", { name: editor.addParameter }));
    expect(screen.getByText(editor.errors.required)).toBeInTheDocument();

    await user.type(screen.getByRole("textbox", { name: "Parameter 1 name" }), "1st");
    expect(screen.getByText(editor.errors.invalidName)).toBeInTheDocument();
  });
});
