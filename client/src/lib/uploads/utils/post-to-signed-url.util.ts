import { ApiError } from "@/lib/api/api-error";
import type { UploadProgress } from "../typing/types/upload-progress.type";
import { UploadCanceledError } from "../upload-canceled-error";
import { createStorageUploadError } from "./create-storage-upload-error.util";
import { createUploadProgress } from "./create-upload-progress.util";

interface Options {
  url: string;
  formData: FormData;
  signal?: AbortSignal;
  onProgress?: (progress: UploadProgress) => void;
}

const isSuccessfulStatus = (status: number): boolean => {
  return status >= 200 && status < 300;
};

const createNetworkError = (): ApiError => {
  return new ApiError({
    status: 0,
    code: "UPLOAD_NOT_COMPLETED",
    message: "The file storage could not be reached.",
  });
};

export const postToSignedUrl = ({ url, formData, signal, onProgress }: Options): Promise<void> => {
  return new Promise<void>((resolve, reject) => {
    const request = new XMLHttpRequest();

    const handleAbort = (): void => {
      request.abort();
      reject(new UploadCanceledError());
    };

    const settle = (finish: () => void): void => {
      signal?.removeEventListener("abort", handleAbort);
      finish();
    };

    request.open("POST", url);
    request.withCredentials = false;
    request.upload.onprogress = (event: ProgressEvent): void => {
      if (event.lengthComputable && onProgress !== undefined) {
        onProgress(createUploadProgress(event.loaded, event.total));
      }
    };
    request.onload = (): void => {
      settle(() => {
        if (isSuccessfulStatus(request.status)) {
          resolve();
          return;
        }

        reject(
          createStorageUploadError({
            status: request.status,
            statusText: request.statusText,
            responseText: request.responseText,
          }),
        );
      });
    };
    request.onerror = (): void => {
      settle(() => {
        reject(createNetworkError());
      });
    };
    request.ontimeout = request.onerror;

    if (signal?.aborted === true) {
      handleAbort();
      return;
    }

    signal?.addEventListener("abort", handleAbort, { once: true });
    request.send(formData);
  });
};
