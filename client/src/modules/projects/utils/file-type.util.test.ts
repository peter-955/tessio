import { describe, expect, it } from "vitest";
import { KNOWN_FILE_TYPES } from "../typing/constants/file-type.constant";
import { buildFileTypeOptions, checkIsValidMimeType } from "./file-type.util";

describe("buildFileTypeOptions", () => {
  it("labels known types with the format and the MIME type", () => {
    const options = buildFileTypeOptions([]);

    expect(options).toHaveLength(KNOWN_FILE_TYPES.length);
    expect(options[0]).toEqual({ value: "image/png", label: "PNG (image/png)" });
  });

  it("adds a selected unknown type labelled with the bare MIME type", () => {
    const options = buildFileTypeOptions(["image/png", "application/x-custom"]);

    expect(options.at(-1)).toEqual({
      value: "application/x-custom",
      label: "application/x-custom",
    });
    expect(options).toHaveLength(KNOWN_FILE_TYPES.length + 1);
  });
});

describe("checkIsValidMimeType", () => {
  it.each(["text/markdown", "application/vnd.ms-excel", "image/svg+xml"])("accepts %s", (value) => {
    expect(checkIsValidMimeType(value)).toBe(true);
  });

  it.each(["markdown", "Text/Markdown", "text/", "text/mark down"])("rejects %s", (value) => {
    expect(checkIsValidMimeType(value)).toBe(false);
  });
});
