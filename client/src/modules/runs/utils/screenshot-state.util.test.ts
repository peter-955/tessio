import { describe, expect, it } from "vitest";
import { resolveScreenshotState } from "./screenshot-state.util";

const FILE_ID = "f1000000-0000-4000-8000-000000000001";

describe("resolveScreenshotState", () => {
  it("is none without a file", () => {
    expect(resolveScreenshotState(null, null, "running")).toBe("none");
  });

  it("is uploaded once the file is verified", () => {
    expect(resolveScreenshotState(FILE_ID, "uploaded", "running")).toBe("uploaded");
    expect(resolveScreenshotState(FILE_ID, "uploaded", "passed")).toBe("uploaded");
  });

  it("is uploading while pending in a running run", () => {
    expect(resolveScreenshotState(FILE_ID, "pending", "running")).toBe("uploading");
  });

  it("is missing when pending after the run ends or marked missing", () => {
    expect(resolveScreenshotState(FILE_ID, "pending", "passed")).toBe("missing");
    expect(resolveScreenshotState(FILE_ID, "pending", "aborted")).toBe("missing");
    expect(resolveScreenshotState(FILE_ID, "missing", "running")).toBe("missing");
    expect(resolveScreenshotState(FILE_ID, null, "failed")).toBe("missing");
  });
});
