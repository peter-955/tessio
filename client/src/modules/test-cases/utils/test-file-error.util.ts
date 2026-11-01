import type { ApiError } from "@/lib/api/api-error";
import type { TestFileErrorKey } from "../typing/types/test-file-error-key.type";

export const findTestFileErrorKey = (error: ApiError): TestFileErrorKey | null => {
  switch (error.code) {
    case "CONFLICT":
      return "fileConflict";
    case "UPLOAD_NOT_COMPLETED":
      return "uploadNotCompleted";
    case "FILE_TYPE_NOT_ALLOWED":
      return "fileTypeNotAllowed";
    case "FILE_TOO_LARGE":
      return "fileTooLarge";
    default:
      return null;
  }
};
