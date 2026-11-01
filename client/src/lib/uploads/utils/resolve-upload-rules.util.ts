import {
  AVATAR_CONTENT_TYPES,
  MAX_AVATAR_SIZE_IN_BYTES,
  MAX_FILE_SIZE_IN_BYTES,
  SCREENSHOT_CONTENT_TYPES,
} from "../typing/constants/upload-limits.constant";
import type { UploadRules } from "../typing/types/upload-rules.type";
import type { UploadTarget } from "../typing/types/upload-target.type";
import { normalizeContentType } from "./normalize-content-type.util";

export const resolveUploadRules = (target: UploadTarget): UploadRules => {
  if (target.kind === "avatar") {
    return { maxSizeInBytes: MAX_AVATAR_SIZE_IN_BYTES, acceptedTypes: [...AVATAR_CONTENT_TYPES] };
  }

  const allowedTypes = target.allowedFileTypes.map(normalizeContentType);
  const acceptedTypes =
    target.kind === "evidence" ? [...allowedTypes, ...SCREENSHOT_CONTENT_TYPES] : allowedTypes;

  return {
    maxSizeInBytes: MAX_FILE_SIZE_IN_BYTES,
    acceptedTypes: [...new Set(acceptedTypes.filter((type) => type !== ""))],
  };
};
