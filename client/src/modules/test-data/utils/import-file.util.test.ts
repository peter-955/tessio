import { describe, expect, it } from "vitest";
import { MAX_IMPORT_SIZE_IN_BYTES } from "../typing/constants/test-data.constant";
import { findImportFileError, prepareImportFile } from "./import-file.util";

const createFile = (name: string, content = "KEY=value", type = ""): File => {
  return new File([content], name, { type });
};

describe("findImportFileError", () => {
  it.each([".env", "local.env", ".env.staging", "data.JSON", "data.yaml", "data.yml"])(
    "accepts %s",
    (name) => {
      expect(findImportFileError(createFile(name))).toBeNull();
    },
  );

  it.each(["notes.txt", "env", "data.csv", "data.json.bak"])("rejects %s", (name) => {
    expect(findImportFileError(createFile(name))).toBe("extension");
  });

  it("rejects a file larger than 1 MB", () => {
    const file = createFile("data.json", "a".repeat(MAX_IMPORT_SIZE_IN_BYTES + 1));

    expect(findImportFileError(file)).toBe("size");
  });

  it("accepts a file of exactly 1 MB", () => {
    const file = createFile("data.json", "a".repeat(MAX_IMPORT_SIZE_IN_BYTES));

    expect(findImportFileError(file)).toBeNull();
  });
});

describe("prepareImportFile", () => {
  it.each([
    [".env", "", "text/plain"],
    [".env.staging", "", "text/plain"],
    ["data.yaml", "application/x-yaml", "text/plain"],
    ["data.yml", "application/x-yaml", "text/plain"],
    ["data.json", "application/json", "application/json"],
    ["DATA.JSON", "", "application/json"],
  ])("types %s as %s", (name, type, expectedType) => {
    const preparedFile = prepareImportFile(createFile(name, "KEY=value", type));

    expect(preparedFile.type).toBe(expectedType);
    expect(preparedFile.name).toBe(name);
    expect(preparedFile.size).toBe("KEY=value".length);
  });
});
