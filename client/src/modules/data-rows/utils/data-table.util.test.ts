import { describe, expect, it } from "vitest";
import {
  addDataParameter,
  addDataRow,
  buildCellKey,
  buildDataRows,
  buildDataTableValues,
  changeDataValue,
  checkAreDataRowsEqual,
  checkAreParametersEqual,
  checkHasDataTableErrors,
  listParameterNames,
  removeDataParameter,
  renameDataParameter,
  validateDataTable,
} from "./data-table.util";

const PARAMETERS = ["email", "role"];

const ROWS = [
  { email: "ann@shop.test", role: "admin" },
  { email: "{{data.qc_email}}", role: "qc" },
];

describe("data table", () => {
  it("round-trips the saved parameters and rows", () => {
    const table = buildDataTableValues(PARAMETERS, ROWS);

    expect(listParameterNames(table)).toEqual(PARAMETERS);
    expect(buildDataRows(table)).toEqual(ROWS);
    expect(checkAreParametersEqual(table, PARAMETERS)).toBe(true);
    expect(checkAreDataRowsEqual(table, ROWS)).toBe(true);
  });

  it("keeps the values when a parameter is renamed", () => {
    const table = buildDataTableValues(PARAMETERS, ROWS);
    const [email] = table.parameters;
    if (email === undefined) {
      throw new Error("The table has parameters.");
    }

    const renamed = renameDataParameter(table, email.id, "login");

    expect(buildDataRows(renamed)).toEqual([
      { login: "ann@shop.test", role: "admin" },
      { login: "{{data.qc_email}}", role: "qc" },
    ]);
    expect(checkAreParametersEqual(renamed, PARAMETERS)).toBe(false);
  });

  it("adds an empty value for a new parameter and a new row", () => {
    const table = addDataRow(addDataParameter(buildDataTableValues(["email"], [{ email: "a" }])));
    const [, added] = table.parameters;
    const [, newRow] = table.rows;
    if (added === undefined || newRow === undefined) {
      throw new Error("The table has a new parameter and row.");
    }

    const filled = changeDataValue(
      renameDataParameter(table, added.id, "role"),
      newRow.id,
      added.id,
      "qc",
    );

    expect(buildDataRows(filled)).toEqual([
      { email: "a", role: "" },
      { email: "", role: "qc" },
    ]);
  });

  it("drops the rows when the last parameter is removed", () => {
    const table = buildDataTableValues(["email"], [{ email: "a" }]);
    const [email] = table.parameters;
    if (email === undefined) {
      throw new Error("The table has a parameter.");
    }

    expect(removeDataParameter(table, email.id)).toEqual({ parameters: [], rows: [] });
  });

  it("flags empty, invalid and repeated names and long values", () => {
    const table = buildDataTableValues(
      ["Email", "email", "", "2fa"],
      [{ Email: "x".repeat(1001), email: "", "": "", "2fa": "" }],
    );
    const [first, second, third, fourth] = table.parameters;
    const [row] = table.rows;
    if (
      first === undefined ||
      second === undefined ||
      third === undefined ||
      fourth === undefined ||
      row === undefined
    ) {
      throw new Error("The table has four parameters and a row.");
    }

    const errors = validateDataTable(table);

    expect(errors.parameters).toEqual({
      [first.id]: "duplicateName",
      [second.id]: "duplicateName",
      [third.id]: "required",
      [fourth.id]: "invalidName",
    });
    expect(errors.values).toEqual({ [buildCellKey(row.id, first.id)]: "tooLong" });
    expect(checkHasDataTableErrors(errors)).toBe(true);
  });

  it("refuses parameters with no data rows, like the server", () => {
    const errors = validateDataTable(buildDataTableValues(PARAMETERS, []));

    expect(errors.table).toBe("parametersWithoutRows");
    expect(checkHasDataTableErrors(errors)).toBe(true);
    expect(validateDataTable(buildDataTableValues([], [])).table).toBeUndefined();
  });

  it("limits the table to 20 parameters and 20 rows", () => {
    const names = Array.from({ length: 21 }, (_, index) => `p${index}`);
    const rows = Array.from({ length: 21 }, () => ({ p0: "x" }));

    expect(validateDataTable(buildDataTableValues(names, [])).table).toBe("tooManyParameters");
    expect(validateDataTable(buildDataTableValues(["p0"], rows)).table).toBe("tooManyRows");
    expect(checkHasDataTableErrors(validateDataTable(buildDataTableValues(PARAMETERS, ROWS)))).toBe(
      false,
    );
  });
});
