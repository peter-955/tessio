import { describe, expect, it } from "vitest";
import { checkIsSameDataTable, formatDataTableText } from "./data-table-text.util";

const PARAMETERS = ["email", "role"];

const FIRST_ROW = { email: "ann@shop.test", role: "admin" };

const ROWS = [FIRST_ROW, { email: "{{data.qc_email}}", role: "qc" }];

describe("formatDataTableText", () => {
  it("writes the parameters, then one numbered line per data row", () => {
    expect(formatDataTableText(PARAMETERS, ROWS)).toBe(
      "email | role\n1. ann@shop.test | admin\n2. {{data.qc_email}} | qc",
    );
  });

  it("is empty for a case without parameters", () => {
    expect(formatDataTableText([], [])).toBe("");
  });
});

describe("checkIsSameDataTable", () => {
  it("is true only for the same parameters in the same order and the same rows", () => {
    const table = { parameters: PARAMETERS, dataRows: ROWS };

    expect(checkIsSameDataTable(table, { parameters: [...PARAMETERS], dataRows: [...ROWS] })).toBe(
      true,
    );
    expect(checkIsSameDataTable(table, { parameters: ["role", "email"], dataRows: ROWS })).toBe(
      false,
    );
    expect(checkIsSameDataTable(table, { parameters: PARAMETERS, dataRows: [FIRST_ROW] })).toBe(
      false,
    );
    expect(
      checkIsSameDataTable(table, {
        parameters: PARAMETERS,
        dataRows: [FIRST_ROW, { email: "{{data.qc_email}}", role: "dev" }],
      }),
    ).toBe(false);
  });
});
