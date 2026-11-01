import type { ApiError } from "@/lib/api/api-error";
import type {
  CaseImportErrorKey,
  CaseImportStage,
} from "../typing/types/case-import-error-key.type";

export const findCaseImportErrorKey = (
  error: ApiError,
  stage: CaseImportStage,
): CaseImportErrorKey | null => {
  switch (error.code) {
    case "IMPORT_INVALID_FILE":
      return "invalidFile";
    case "FILE_TOO_LARGE":
      return "size";
    case "UPLOAD_NOT_COMPLETED":
      return "uploadNotCompleted";
    case "NOT_FOUND":
      return "notFound";
    case "FILE_TYPE_NOT_ALLOWED":
      return "typeNotAllowed";
    case "INVALID_REQUEST":
      return stage === "commit" ? "choiceInvalid" : "invalidFile";
    default:
      return null;
  }
};
