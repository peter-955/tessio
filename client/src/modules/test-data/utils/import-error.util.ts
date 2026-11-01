import type { ApiError } from "@/lib/api/api-error";
import type { ImportErrorKey } from "../typing/types/import-error-key.type";

export const findImportErrorKey = (error: ApiError): ImportErrorKey | null => {
  switch (error.code) {
    case "FILE_TYPE_NOT_ALLOWED":
      return "typeNotAllowed";
    case "IMPORT_INVALID_FILE":
      return "invalidFile";
    case "FILE_TOO_LARGE":
      return "size";
    case "UPLOAD_NOT_COMPLETED":
      return "uploadNotCompleted";
    default:
      return null;
  }
};
