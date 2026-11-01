import { UploadCanceledError } from "../upload-canceled-error";

export const throwIfUploadCanceled = (signal: AbortSignal | undefined): void => {
  if (signal?.aborted === true) {
    throw new UploadCanceledError();
  }
};
