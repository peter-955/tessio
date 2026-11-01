import { ApiError } from "@/lib/api/api-error";
import { S3_ERROR_CODE_PATTERN } from "../typing/constants/upload-form.constant";

interface Options {
  status: number;
  statusText: string;
  responseText: string;
}

export const createStorageUploadError = ({
  status,
  statusText,
  responseText,
}: Options): ApiError => {
  const storageCode = S3_ERROR_CODE_PATTERN.exec(responseText)?.[1]?.trim() ?? null;

  if (storageCode === "EntityTooLarge") {
    return new ApiError({ status: 413, code: "FILE_TOO_LARGE", message: "The file is too large." });
  }

  if (storageCode === "EntityTooSmall") {
    return new ApiError({ status: 422, code: "INVALID_REQUEST", message: "The file is empty." });
  }

  return new ApiError({
    status,
    code: "UPLOAD_NOT_COMPLETED",
    message: storageCode ?? (statusText || String(status)),
  });
};
