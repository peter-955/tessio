import { describe, expect, it } from "vitest";
import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import {
  MAX_AVATAR_SIZE_IN_BYTES,
  MAX_FILE_SIZE_IN_BYTES,
} from "../typing/constants/upload-limits.constant";
import { resolveUploadRules } from "./resolve-upload-rules.util";

describe("resolveUploadRules", () => {
  it("returns the avatar size limit and image types", () => {
    expect(resolveUploadRules(AVATAR_UPLOAD_TARGET)).toEqual({
      maxSizeInBytes: MAX_AVATAR_SIZE_IN_BYTES,
      acceptedTypes: ["image/jpeg", "image/png", "image/webp"],
    });
  });

  it("normalizes the project file types", () => {
    const rules = resolveUploadRules({
      kind: "test_file",
      projectKey: "TES",
      allowedFileTypes: ["Text/CSV; charset=utf-8", " application/PDF "],
    });

    expect(rules).toEqual({
      maxSizeInBytes: MAX_FILE_SIZE_IN_BYTES,
      acceptedTypes: ["text/csv", "application/pdf"],
    });
  });

  it("adds the screenshot types once for evidence", () => {
    const rules = resolveUploadRules({
      kind: "evidence",
      projectKey: "TES",
      allowedFileTypes: ["application/pdf", "IMAGE/PNG"],
    });

    expect(rules.acceptedTypes).toEqual([
      "application/pdf",
      "image/png",
      "image/jpeg",
      "image/webp",
    ]);
  });

  it.each(["test_file", "import"] as const)("does not add the screenshot types for %s", (kind) => {
    const rules = resolveUploadRules({
      kind,
      projectKey: "TES",
      allowedFileTypes: ["text/csv"],
    });

    expect(rules.acceptedTypes).toEqual(["text/csv"]);
  });
});
