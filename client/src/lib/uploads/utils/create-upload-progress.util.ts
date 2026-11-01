import type { UploadProgress } from "../typing/types/upload-progress.type";

export const createUploadProgress = (loadedBytes: number, totalBytes: number): UploadProgress => {
  return {
    loadedBytes,
    totalBytes,
    percent: totalBytes === 0 ? 0 : Math.round((loadedBytes / totalBytes) * 100),
  };
};
