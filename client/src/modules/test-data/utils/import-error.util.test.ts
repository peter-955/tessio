import { ApiError } from "@/lib/api/api-error";
import type { ApiErrorCode } from "@/lib/api/typing/types/api-error-code.type";
import { describe, expect, it } from "vitest";
import { findImportErrorKey } from "./import-error.util";

const createError = (code: ApiErrorCode | null): ApiError => {
  return new ApiError({ status: 422, code, message: "failed" });
};

describe("findImportErrorKey", () => {
  it.each([
    ["FILE_TYPE_NOT_ALLOWED", "typeNotAllowed"],
    ["IMPORT_INVALID_FILE", "invalidFile"],
    ["FILE_TOO_LARGE", "size"],
    ["UPLOAD_NOT_COMPLETED", "uploadNotCompleted"],
  ] as const)("maps %s to %s", (code, key) => {
    expect(findImportErrorKey(createError(code))).toBe(key);
  });

  it("leaves other errors to the generic message", () => {
    expect(findImportErrorKey(createError("PERMISSION_DENIED"))).toBeNull();
    expect(findImportErrorKey(createError(null))).toBeNull();
  });
});
