import { apiClient } from "@/lib/api/api-client";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import type { SignedUpload } from "../typing/types/signed-upload.type";
import type { UploadTarget } from "../typing/types/upload-target.type";
import { normalizeContentType } from "./normalize-content-type.util";

export const requestSignedUpload = (
  target: UploadTarget,
  file: File,
  contentType: string,
): Promise<SignedUpload> => {
  const body = {
    fileName: file.name,
    contentType: normalizeContentType(contentType),
    size: file.size,
  };

  if (target.kind === "avatar") {
    return unwrapResponse<SignedUpload>(apiClient.POST("/api/me/avatar-upload", { body }));
  }

  return unwrapResponse<SignedUpload>(
    apiClient.POST("/api/projects/{project_key}/uploads", {
      params: { path: { project_key: target.projectKey } },
      body: { ...body, kind: target.kind },
    }),
  );
};
