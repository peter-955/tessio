"use client";

import { DSModal } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useSignedUpload } from "@/lib/uploads/hooks/use-signed-upload";
import { UploadCanceledError } from "@/lib/uploads/upload-canceled-error";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostCaseImportCommit } from "../../hooks/mutations/use-post-case-import-commit";
import { usePostCaseImportPreview } from "../../hooks/mutations/use-post-case-import-preview";
import type { CaseImportStage } from "../../typing/types/case-import-error-key.type";
import type { CaseImportRow } from "../../typing/types/case-import-row.type";
import type { CaseImportStep } from "../../typing/types/case-import-step.type";
import type { CaseImportPreview } from "../../typing/types/test-case.type";
import { findCaseImportErrorKey } from "../../utils/import-error.util";
import { findCaseImportFileError, prepareCaseImportFile } from "../../utils/import-file.util";
import { buildCaseImportRows, readIncludedCaseImportIndexes } from "../../utils/import-rows.util";
import { ImportFileStep } from "./import-file-step/import-file-step";
import { ImportPreviewStep } from "./import-preview-step/import-preview-step";

interface Props {
  onClose: () => void;
}

interface PreviewState {
  fileId: string;
  preview: CaseImportPreview;
}

export const ImportWizard: FC<Props> = ({ onClose }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const [step, setStep] = useState<CaseImportStep>("file");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [previewState, setPreviewState] = useState<PreviewState | null>(null);
  const [rows, setRows] = useState<CaseImportRow[]>([]);
  const signedUpload = useSignedUpload({
    target: {
      kind: "import",
      projectKey: project.key,
      allowedFileTypes: project.allowedFileTypes,
    },
    isGlobalErrorToastDisabled: true,
  });
  const previewImport = usePostCaseImportPreview(project.key, {
    isGlobalErrorToastDisabled: true,
  });

  const translateError = (error: unknown, stage: CaseImportStage): string => {
    if (!(error instanceof ApiError)) {
      return resolveMessage(error);
    }

    const errorKey = findCaseImportErrorKey(error, stage);

    return errorKey === null ? resolveMessage(error) : t(`import.errors.${errorKey}`);
  };

  const commitImport = usePostCaseImportCommit(project.key, {
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      setErrorMessage(translateError(error, "commit"));
    },
    onSuccess: (result) => {
      showSuccessToast(t("toasts.imported", { count: result.created.length }));
      signedUpload.reset();
      onClose();
    },
  });
  const isBusy = signedUpload.isUploading || previewImport.isPending || commitImport.isPending;
  const includedIndexes = readIncludedCaseImportIndexes(rows);

  const handleFileSelected = async (file: File): Promise<void> => {
    const fileError = findCaseImportFileError(file);
    if (fileError !== null) {
      setErrorMessage(t(`import.errors.${fileError}`));
      return;
    }

    setErrorMessage(null);

    try {
      const uploadedFile = await signedUpload.upload(prepareCaseImportFile(file));
      const preview = await previewImport.mutateAsync({ fileId: uploadedFile.id });
      setPreviewState({ fileId: uploadedFile.id, preview });
      setRows(buildCaseImportRows(preview.items));
      setStep("preview");
    } catch (error) {
      if (!(error instanceof UploadCanceledError)) {
        setErrorMessage(translateError(error, "preview"));
      }
    }
  };

  const handleBack = (): void => {
    signedUpload.reset();
    previewImport.reset();
    commitImport.reset();
    setPreviewState(null);
    setRows([]);
    setErrorMessage(null);
    setStep("file");
  };

  const handleClose = (): void => {
    signedUpload.reset();
    onClose();
  };

  const handleCommit = (): void => {
    if (previewState === null) {
      return;
    }

    setErrorMessage(null);
    commitImport.mutate({ fileId: previewState.fileId, indexes: includedIndexes });
  };

  return (
    <DSModal
      isOpened
      onClose={handleClose}
      title={t("import.title")}
      isCloseDisabled={isBusy}
      action={
        step === "preview"
          ? {
              label: t("import.commit", { count: includedIndexes.length }),
              icon: "upload",
              isLoading: commitImport.isPending,
              isDisabled: includedIndexes.length === 0,
              onClick: handleCommit,
            }
          : undefined
      }
    >
      {step === "file" || previewState === null ? (
        <ImportFileStep
          onFileSelected={(file) => {
            void handleFileSelected(file);
          }}
          errorMessage={errorMessage}
          uploadPercent={signedUpload.progress?.percent ?? null}
          isUploading={signedUpload.isUploading}
          isReading={previewImport.isPending}
          onCancelUpload={signedUpload.cancel}
        />
      ) : (
        <ImportPreviewStep
          preview={previewState.preview}
          rows={rows}
          isBusy={isBusy}
          errorMessage={errorMessage}
          onRowsChange={setRows}
          onBack={handleBack}
        />
      )}
    </DSModal>
  );
};
