"use client";

import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useAppMutation } from "@/shared/hooks/use-app-mutation";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AVATAR_UPLOAD_TARGET } from "../typing/constants/avatar-upload-target.constant";
import { ACTIVE_UPLOAD_PHASES } from "../typing/constants/upload-phase.constant";
import { ALLOWED_FILE_TYPES_SEPARATOR } from "../typing/constants/upload-target-key.constant";
import { UploadPhase } from "../typing/enums/upload-phase.enum";
import type { UploadProgress } from "../typing/types/upload-progress.type";
import type { UploadRules } from "../typing/types/upload-rules.type";
import type { UploadTarget } from "../typing/types/upload-target.type";
import type { UploadedFile } from "../typing/types/uploaded-file.type";
import { UploadCanceledError } from "../upload-canceled-error";
import { resolveUploadRules } from "../utils/resolve-upload-rules.util";
import { runSignedUpload } from "../utils/run-signed-upload.util";

export interface UseSignedUploadOptions {
  target: UploadTarget;
  apiErrors?: ApiErrorMessages;
  isGlobalErrorToastDisabled?: boolean;
  onSuccess?: (file: UploadedFile) => void;
}

export interface UseSignedUploadResult {
  upload: (file: File) => Promise<UploadedFile>;
  cancel: () => void;
  reset: () => void;
  phase: UploadPhase;
  progress: UploadProgress | null;
  uploadedFile: UploadedFile | undefined;
  error: ApiError | null;
  isUploading: boolean;
  rules: UploadRules;
}

export const useSignedUpload = ({
  target,
  apiErrors,
  isGlobalErrorToastDisabled = false,
  onSuccess,
}: UseSignedUploadOptions): UseSignedUploadResult => {
  const [phase, setPhase] = useState<UploadPhase>(UploadPhase.IDLE);
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { showErrorToast } = useShowToast();
  const resolveMessage = useResolveApiErrorMessage();

  const targetKind = target.kind;
  const projectKey = target.kind === "avatar" ? null : target.projectKey;
  const allowedFileTypesKey =
    target.kind === "avatar" ? "" : target.allowedFileTypes.join(ALLOWED_FILE_TYPES_SEPARATOR);

  const rules = useMemo((): UploadRules => {
    if (targetKind === "avatar" || projectKey === null) {
      return resolveUploadRules(AVATAR_UPLOAD_TARGET);
    }

    return resolveUploadRules({
      kind: targetKind,
      projectKey,
      allowedFileTypes: allowedFileTypesKey.split(ALLOWED_FILE_TYPES_SEPARATOR),
    });
  }, [targetKind, projectKey, allowedFileTypesKey]);

  const mutation = useAppMutation<UploadedFile, File>({
    isGlobalErrorToastDisabled: true,
    mutationFn: async (file) => {
      abortControllerRef.current?.abort();
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      const isCurrentUpload = (): boolean => {
        return abortControllerRef.current === abortController;
      };

      setProgress(null);

      try {
        const uploadedFile = await runSignedUpload({
          target,
          file,
          signal: abortController.signal,
          onPhaseChange: (nextPhase) => {
            if (isCurrentUpload()) {
              setPhase(nextPhase);
            }
          },
          onProgress: (nextProgress) => {
            if (isCurrentUpload()) {
              setProgress(nextProgress);
            }
          },
        });

        if (isCurrentUpload()) {
          setPhase(UploadPhase.UPLOADED);
        }

        return uploadedFile;
      } catch (error) {
        if (isCurrentUpload()) {
          setPhase(
            error instanceof UploadCanceledError ? UploadPhase.CANCELED : UploadPhase.FAILED,
          );
        }

        throw error;
      }
    },
    onSuccess: (uploadedFile) => {
      onSuccess?.(uploadedFile);
    },
    onError: (error) => {
      if (error instanceof UploadCanceledError || isGlobalErrorToastDisabled) {
        return;
      }

      showErrorToast(resolveMessage(error, apiErrors));
    },
  });

  const { mutateAsync, reset: resetMutation } = mutation;

  const cancel = useCallback((): void => {
    abortControllerRef.current?.abort();
  }, []);

  const reset = useCallback((): void => {
    const abortController = abortControllerRef.current;
    abortControllerRef.current = null;
    abortController?.abort();
    resetMutation();
    setPhase(UploadPhase.IDLE);
    setProgress(null);
  }, [resetMutation]);

  useEffect(() => {
    return (): void => {
      abortControllerRef.current?.abort();
    };
  }, []);

  return {
    upload: mutateAsync,
    cancel,
    reset,
    phase,
    progress,
    uploadedFile: mutation.data,
    error: mutation.error,
    isUploading: ACTIVE_UPLOAD_PHASES.includes(phase),
    rules,
  };
};
