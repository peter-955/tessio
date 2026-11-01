import type { UseSignedUploadResult } from "@/lib/uploads/hooks/use-signed-upload";
import { UploadPhase } from "@/lib/uploads/typing/enums/upload-phase.enum";
import type { UploadedFile } from "@/lib/uploads/typing/types/uploaded-file.type";
import { vi } from "vitest";

export const IMPORT_FILE_ID = "f1000000-0000-4000-8000-000000000001";

export const uploadFile = vi.fn<(file: File) => Promise<UploadedFile>>();

export const resetUpload = vi.fn<() => void>();

export const cancelUpload = vi.fn<() => void>();

export const buildUploadedFile = (file: File): UploadedFile => {
  return {
    id: IMPORT_FILE_ID,
    kind: "import",
    fileName: file.name,
    contentType: file.type,
    size: file.size,
    status: "uploaded",
    createdAt: "2026-10-01T09:00:00Z",
  };
};

export const signedUploadMock = {
  useSignedUpload: (): UseSignedUploadResult => {
    return {
      upload: uploadFile,
      cancel: cancelUpload,
      reset: resetUpload,
      phase: UploadPhase.IDLE,
      progress: null,
      uploadedFile: undefined,
      error: null,
      isUploading: false,
      rules: { maxSizeInBytes: 20971520, acceptedTypes: ["text/plain", "application/json"] },
    };
  },
};
