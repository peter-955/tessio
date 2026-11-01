import { CONTENT_TYPE_FIELD, FILE_FIELD } from "../typing/constants/upload-form.constant";
import type { SignedUpload } from "../typing/types/signed-upload.type";

export const buildUploadFormData = (
  signedUpload: SignedUpload,
  file: File,
  contentType: string,
): FormData => {
  const formData = new FormData();

  Object.entries(signedUpload.fields).forEach(([name, value]) => {
    formData.append(name, value);
  });
  formData.append(CONTENT_TYPE_FIELD, contentType);
  formData.append(FILE_FIELD, file);

  return formData;
};
