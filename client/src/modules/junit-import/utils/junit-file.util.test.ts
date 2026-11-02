import { describe, expect, it } from "vitest";
import { MAX_JUNIT_FILE_BYTES } from "../typing/constants/junit-import.constant";
import { findJunitFileError } from "./junit-file.util";

describe("findJunitFileError", () => {
  it("accepts an XML file up to 10 MB", () => {
    expect(findJunitFileError({ name: "results.XML", size: MAX_JUNIT_FILE_BYTES })).toBeNull();
  });

  it("refuses a file that is not .xml", () => {
    expect(findJunitFileError({ name: "results.json", size: 10 })).toBe("notXml");
  });

  it("refuses an empty file and a file over 10 MB", () => {
    expect(findJunitFileError({ name: "results.xml", size: 0 })).toBe("empty");
    expect(findJunitFileError({ name: "results.xml", size: MAX_JUNIT_FILE_BYTES + 1 })).toBe(
      "tooLarge",
    );
  });
});
