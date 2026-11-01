import { describe, expect, it } from "vitest";
import {
  CSV_CONTENT_TYPE,
  MAX_CASE_IMPORT_SIZE_IN_BYTES,
  XLSX_CONTENT_TYPE,
} from "../typing/constants/test-case.constant";
import { findCaseImportFileError, prepareCaseImportFile } from "./import-file.util";

const createFile = (name: string, content = "Story,Title", type = ""): File => {
  return new File([content], name, { type });
};

describe("findCaseImportFileError", () => {
  it.each(["cases.xlsx", "CASES.XLSX", "cases.csv"])("accepts %s", (name) => {
    expect(findCaseImportFileError(createFile(name))).toBeNull();
  });

  it.each(["cases.xls", "cases.txt", "cases.csv.bak", "xlsx"])("rejects %s", (name) => {
    expect(findCaseImportFileError(createFile(name))).toBe("extension");
  });

  it("rejects a file over 5 MB and accepts exactly 5 MB", () => {
    expect(
      findCaseImportFileError(
        createFile("cases.csv", "a".repeat(MAX_CASE_IMPORT_SIZE_IN_BYTES + 1)),
      ),
    ).toBe("size");
    expect(
      findCaseImportFileError(createFile("cases.csv", "a".repeat(MAX_CASE_IMPORT_SIZE_IN_BYTES))),
    ).toBeNull();
  });
});

describe("prepareCaseImportFile", () => {
  it.each([
    ["cases.xlsx", "", XLSX_CONTENT_TYPE],
    ["cases.csv", "application/vnd.ms-excel", CSV_CONTENT_TYPE],
    ["CASES.CSV", "", CSV_CONTENT_TYPE],
  ])("types %s as %s", (name, type, expectedType) => {
    const preparedFile = prepareCaseImportFile(createFile(name, "Story,Title", type));

    expect(preparedFile.type).toBe(expectedType);
    expect(preparedFile.name).toBe(name);
    expect(preparedFile.size).toBe("Story,Title".length);
  });
});
