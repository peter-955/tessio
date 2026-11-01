import type { ApiError } from "@/lib/api/api-error";
import type { TestCaseSaveError } from "../typing/types/test-case-save-error.type";

export const findTestCaseSaveError = (error: ApiError): TestCaseSaveError | null => {
  if (error.code === "CONFLICT") {
    return "versionConflict";
  }

  if (error.code === "INVALID_REQUEST" && Object.keys(error.fieldErrors).length === 0) {
    return "criterionNotLinkable";
  }

  return null;
};
