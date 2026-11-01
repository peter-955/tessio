import { UploadPhase } from "../typing/enums/upload-phase.enum";
import type { UploadProgress } from "../typing/types/upload-progress.type";
import type { UploadTarget } from "../typing/types/upload-target.type";
import type { UploadedFile } from "../typing/types/uploaded-file.type";
import { buildUploadFormData } from "./build-upload-form-data.util";
import { completeSignedUpload } from "./complete-signed-upload.util";
import { createUploadProgress } from "./create-upload-progress.util";
import { findUploadFileError } from "./find-upload-file-error.util";
import { postToSignedUrl } from "./post-to-signed-url.util";
import { requestSignedUpload } from "./request-signed-upload.util";
import { resolveFileContentType } from "./resolve-file-content-type.util";
import { resolveUploadRules } from "./resolve-upload-rules.util";
import { throwIfUploadCanceled } from "./throw-if-upload-canceled.util";

interface Options {
  target: UploadTarget;
  file: File;
  signal?: AbortSignal;
  onPhaseChange?: (phase: UploadPhase) => void;
  onProgress?: (progress: UploadProgress) => void;
}

export const runSignedUpload = async ({
  target,
  file,
  signal,
  onPhaseChange,
  onProgress,
}: Options): Promise<UploadedFile> => {
  const rules = resolveUploadRules(target);
  const contentType = resolveFileContentType(file);
  const fileError = findUploadFileError(file, rules);
  if (fileError !== null) {
    throw fileError;
  }

  throwIfUploadCanceled(signal);
  onPhaseChange?.(UploadPhase.SIGNING);
  const signedUpload = await requestSignedUpload(target, file, contentType);

  throwIfUploadCanceled(signal);
  onPhaseChange?.(UploadPhase.UPLOADING);
  onProgress?.(createUploadProgress(0, file.size));
  await postToSignedUrl({
    url: signedUpload.url,
    formData: buildUploadFormData(signedUpload, file, contentType),
    signal,
    onProgress,
  });

  throwIfUploadCanceled(signal);
  onPhaseChange?.(UploadPhase.COMPLETING);
  const uploadedFile = await completeSignedUpload(target, signedUpload.fileId);

  onProgress?.(createUploadProgress(file.size, file.size));

  return uploadedFile;
};
