"use client";

import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import {
  useSignedUpload,
  type UseSignedUploadOptions,
  type UseSignedUploadResult,
} from "./use-signed-upload";

export const useAvatarUpload = (
  options: Omit<UseSignedUploadOptions, "target"> = {},
): UseSignedUploadResult => {
  return useSignedUpload({ ...options, target: AVATAR_UPLOAD_TARGET });
};
