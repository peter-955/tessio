import { FALLBACK_CONTENT_TYPE } from "../typing/constants/upload-form.constant";
import { normalizeContentType } from "./normalize-content-type.util";

export const resolveFileContentType = (file: File): string => {
  const contentType = normalizeContentType(file.type);

  return contentType === "" ? FALLBACK_CONTENT_TYPE : contentType;
};
