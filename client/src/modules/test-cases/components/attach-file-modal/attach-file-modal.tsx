"use client";

import {
  DSAlert,
  DSButton,
  DSDropzone,
  DSInput,
  DSModal,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useSignedUpload } from "@/lib/uploads/hooks/use-signed-upload";
import { UploadCanceledError } from "@/lib/uploads/upload-canceled-error";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostTestFile } from "../../hooks/mutations/use-post-test-file";
import { FILE_KEY_PATTERN } from "../../typing/constants/test-case.constant";
import type { TestCaseDetail, TestFile } from "../../typing/types/test-case.type";
import { buildFileReference } from "../../utils/file-reference.util";
import { findTestFileErrorKey } from "../../utils/test-file-error.util";
import styles from "./attach-file-modal.module.scss";

interface Props {
  detail: TestCaseDetail;
  existingFile: TestFile | null;
  onClose: () => void;
}

export const AttachFileModal: FC<Props> = ({ detail, existingFile, onClose }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const [fileKey, setFileKey] = useState(existingFile?.key ?? "");
  const [keyError, setKeyError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const signedUpload = useSignedUpload({
    target: {
      kind: "test_file",
      projectKey: project.key,
      allowedFileTypes: project.allowedFileTypes,
    },
    isGlobalErrorToastDisabled: true,
  });
  const attachFile = usePostTestFile(project.key, detail.code, {
    isGlobalErrorToastDisabled: true,
  });
  const trimmedKey = fileKey.trim();
  const matchingFile =
    existingFile ??
    detail.files.find((file) => {
      return file.key === trimmedKey;
    }) ??
    null;
  const isBusy = signedUpload.isUploading || attachFile.isPending;

  const translateError = (error: unknown): string => {
    if (!(error instanceof ApiError)) {
      return resolveMessage(error);
    }

    const errorKey = findTestFileErrorKey(error);

    return errorKey === null ? resolveMessage(error) : t(`errors.${errorKey}`);
  };

  const buildKeyDescription = (): string | undefined => {
    if (matchingFile !== null) {
      return t("files.newVersionHint", {
        number: matchingFile.currentVersion.number + 1,
        key: matchingFile.key,
      });
    }

    return trimmedKey === ""
      ? undefined
      : t("files.keyHint", { reference: buildFileReference(trimmedKey) });
  };

  const handleKeyChange = (value: string): void => {
    setFileKey(value);
    setKeyError(null);
  };

  const handleDrop = async (files: File[]): Promise<void> => {
    const [file] = files;
    if (file === undefined) {
      return;
    }

    if (!FILE_KEY_PATTERN.test(trimmedKey)) {
      setKeyError(t("files.keyInvalid"));
      return;
    }

    setErrorMessage(null);

    try {
      const uploadedFile = await signedUpload.upload(file);
      await attachFile.mutateAsync({
        key: trimmedKey,
        fileId: uploadedFile.id,
        baseVersionNumber: detail.currentVersion.number,
      });
      showSuccessToast(t("toasts.fileAttached", { key: trimmedKey }));
      signedUpload.reset();
      onClose();
    } catch (error) {
      if (!(error instanceof UploadCanceledError)) {
        setErrorMessage(translateError(error));
      }
    }
  };

  const handleClose = (): void => {
    signedUpload.reset();
    onClose();
  };

  return (
    <DSModal
      isOpened
      onClose={handleClose}
      title={existingFile === null ? t("files.title") : t("actions.newVersion")}
      isCloseDisabled={isBusy}
    >
      <DSStack gap={4}>
        <DSInput
          label={t("files.key")}
          value={fileKey}
          onChange={handleKeyChange}
          description={buildKeyDescription()}
          error={keyError ?? undefined}
          autoComplete="off"
          isRequired
          isDisabled={existingFile !== null || isBusy}
          isAutoFocused={existingFile === null}
        />
        <DSDropzone
          title={t("files.dropTitle")}
          description={t("files.dropDescription")}
          onDrop={(files) => {
            void handleDrop(files);
          }}
          acceptedTypes={signedUpload.rules.acceptedTypes}
          isMultiple={false}
          isLoading={isBusy}
        />
        {signedUpload.isUploading && (
          <div className={styles.progress} role="status">
            <DSText size="sm">
              {t("files.uploading", { percent: signedUpload.progress?.percent ?? 0 })}
            </DSText>
            <DSButton type="ghost" size="sm" onClick={signedUpload.cancel}>
              {t("actions.cancelUpload")}
            </DSButton>
          </div>
        )}
        {attachFile.isPending && (
          <div role="status">
            <DSText size="sm">{t("files.attaching")}</DSText>
          </div>
        )}
        {errorMessage !== null && <DSAlert color="danger">{errorMessage}</DSAlert>}
      </DSStack>
    </DSModal>
  );
};
