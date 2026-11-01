import { ApiError } from "@/lib/api/api-error";
import type { UploadRules } from "../typing/types/upload-rules.type";
import { resolveFileContentType } from "./resolve-file-content-type.util";

export const findUploadFileError = (file: File, rules: UploadRules): ApiError | null => {
  if (file.size === 0) {
    return new ApiError({ status: 422, code: "INVALID_REQUEST", message: "The file is empty." });
  }

  if (file.size > rules.maxSizeInBytes) {
    return new ApiError({ status: 413, code: "FILE_TOO_LARGE", message: "The file is too large." });
  }

  if (!rules.acceptedTypes.includes(resolveFileContentType(file))) {
    return new ApiError({
      status: 422,
      code: "FILE_TYPE_NOT_ALLOWED",
      message: "This file type is not allowed.",
    });
  }

  return null;
};
