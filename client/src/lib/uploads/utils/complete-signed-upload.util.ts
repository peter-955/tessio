import { apiClient } from "@/lib/api/api-client";
import { unwrapResponse } from "@/lib/api/utils/unwrap-response.util";
import type { UploadTarget } from "../typing/types/upload-target.type";
import type { UploadedFile } from "../typing/types/uploaded-file.type";

export const completeSignedUpload = (
  target: UploadTarget,
  fileId: string,
): Promise<UploadedFile> => {
  if (target.kind === "avatar") {
    return unwrapResponse<UploadedFile>(
      apiClient.POST("/api/me/avatar-upload/{file_id}/complete", {
        params: { path: { file_id: fileId } },
      }),
    );
  }

  return unwrapResponse<UploadedFile>(
    apiClient.POST("/api/projects/{project_key}/uploads/{file_id}/complete", {
      params: { path: { project_key: target.projectKey, file_id: fileId } },
    }),
  );
};
