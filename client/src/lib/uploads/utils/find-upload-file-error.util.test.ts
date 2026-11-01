import { ApiError } from "@/lib/api/api-error";
import { describe, expect, it } from "vitest";
import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import {
  MAX_AVATAR_SIZE_IN_BYTES,
  MAX_FILE_SIZE_IN_BYTES,
} from "../typing/constants/upload-limits.constant";
import type { UploadRules } from "../typing/types/upload-rules.type";
import { findUploadFileError } from "./find-upload-file-error.util";
import { resolveUploadRules } from "./resolve-upload-rules.util";

const projectRules: UploadRules = resolveUploadRules({
  kind: "test_file",
  projectKey: "TES",
  allowedFileTypes: ["image/png", "application/pdf"],
});

const createFileOfSize = (size: number, type: string, name = "file.bin"): File => {
  const file = new File(["x"], name, { type });
  Object.defineProperty(file, "size", { value: size });

  return file;
};

describe("findUploadFileError", () => {
  it("accepts a file of exactly 20 MB", () => {
    expect(
      findUploadFileError(createFileOfSize(MAX_FILE_SIZE_IN_BYTES, "image/png"), projectRules),
    ).toBeNull();
  });

  it("rejects a file one byte over 20 MB", () => {
    const error = findUploadFileError(
      createFileOfSize(MAX_FILE_SIZE_IN_BYTES + 1, "image/png"),
      projectRules,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 413, code: "FILE_TOO_LARGE" });
  });

  it("rejects an avatar over 2 MB", () => {
    const error = findUploadFileError(
      createFileOfSize(MAX_AVATAR_SIZE_IN_BYTES + 1, "image/png"),
      resolveUploadRules(AVATAR_UPLOAD_TARGET),
    );

    expect(error).toMatchObject({ status: 413, code: "FILE_TOO_LARGE" });
  });

  it("rejects a type the project does not allow", () => {
    const error = findUploadFileError(createFileOfSize(10, "text/html"), projectRules);

    expect(error).toMatchObject({ status: 422, code: "FILE_TYPE_NOT_ALLOWED" });
  });

  it("normalizes the file type before checking it", () => {
    expect(
      findUploadFileError(createFileOfSize(10, "Image/PNG; charset=x"), projectRules),
    ).toBeNull();
  });

  it("rejects an empty file", () => {
    const error = findUploadFileError(
      new File([], "empty.png", { type: "image/png" }),
      projectRules,
    );

    expect(error).toMatchObject({ status: 422, code: "INVALID_REQUEST" });
  });

  it("checks the size before the type", () => {
    const error = findUploadFileError(
      createFileOfSize(MAX_FILE_SIZE_IN_BYTES + 1, "text/html"),
      projectRules,
    );

    expect(error).toMatchObject({ code: "FILE_TOO_LARGE" });
  });

  it("checks a file without a type as application/octet-stream", () => {
    const file = createFileOfSize(10, "");

    expect(findUploadFileError(file, projectRules)).toMatchObject({
      code: "FILE_TYPE_NOT_ALLOWED",
    });
    expect(
      findUploadFileError(file, {
        maxSizeInBytes: MAX_FILE_SIZE_IN_BYTES,
        acceptedTypes: ["application/octet-stream"],
      }),
    ).toBeNull();
  });
});
