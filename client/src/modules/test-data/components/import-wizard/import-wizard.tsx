"use client";

import { DSModal, type DSSelectOption } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useSignedUpload } from "@/lib/uploads/hooks/use-signed-upload";
import { UploadCanceledError } from "@/lib/uploads/upload-canceled-error";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostImportCommit } from "../../hooks/mutations/use-post-import-commit";
import { usePostImportPreview } from "../../hooks/mutations/use-post-import-preview";
import { PROJECT_SCOPE_ID } from "../../typing/constants/test-data.constant";
import type { Environment } from "../../typing/types/environment.type";
import type { ImportRow } from "../../typing/types/import-row.type";
import type { ImportStep } from "../../typing/types/import-step.type";
import type { ImportPreview } from "../../typing/types/import.type";
import { findImportErrorKey } from "../../utils/import-error.util";
import { findImportFileError, prepareImportFile } from "../../utils/import-file.util";
import { buildImportRows } from "../../utils/import-rows.util";
import { ImportFileStep } from "./import-file-step/import-file-step";
import { ImportPreviewStep } from "./import-preview-step/import-preview-step";

interface Props {
  environments: readonly Environment[];
  onClose: () => void;
}

interface PreviewState {
  fileId: string;
  preview: ImportPreview;
}

export const ImportWizard: FC<Props> = ({ environments, onClose }) => {
  const { t } = useTranslation("testData");
  const project = useCurrentProject();
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const canEditSecrets = checkHasProjectCapability(project, "secret.edit");
  const [step, setStep] = useState<ImportStep>("file");
  const [scopeId, setScopeId] = useState(PROJECT_SCOPE_ID);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [previewState, setPreviewState] = useState<PreviewState | null>(null);
  const [rows, setRows] = useState<ImportRow[]>([]);
  const signedUpload = useSignedUpload({
    target: {
      kind: "import",
      projectKey: project.key,
      allowedFileTypes: project.allowedFileTypes,
    },
    isGlobalErrorToastDisabled: true,
  });
  const previewImport = usePostImportPreview(project.key, { isGlobalErrorToastDisabled: true });
  const commitImport = usePostImportCommit(project.key, {
    isGlobalErrorToastDisabled: true,
    onError: (error) => {
      setErrorMessage(resolveMessage(error));
    },
    onSuccess: (result) => {
      showSuccessToast(t("toasts.imported", result));
      signedUpload.reset();
      onClose();
    },
  });
  const isBusy = signedUpload.isUploading || previewImport.isPending || commitImport.isPending;
  const environmentId = scopeId === PROJECT_SCOPE_ID ? null : scopeId;

  const scopeOptions: DSSelectOption<string>[] = [
    { value: PROJECT_SCOPE_ID, label: t("grid.allEnvironments") },
    ...environments
      .filter((environment) => !environment.isArchived)
      .map((environment) => {
        return { value: environment.id, label: environment.name };
      }),
  ];
  const scopeName =
    scopeOptions.find((option) => option.value === scopeId)?.label ?? t("grid.allEnvironments");

  const translateError = (error: unknown): string => {
    if (!(error instanceof ApiError)) {
      return resolveMessage(error);
    }

    const errorKey = findImportErrorKey(error);

    return errorKey === null ? resolveMessage(error) : t(`import.errors.${errorKey}`);
  };

  const handleFileSelected = async (file: File): Promise<void> => {
    const fileError = findImportFileError(file);
    if (fileError !== null) {
      setErrorMessage(t(`import.errors.${fileError}`));
      return;
    }

    setErrorMessage(null);

    try {
      const uploadedFile = await signedUpload.upload(prepareImportFile(file));
      const preview = await previewImport.mutateAsync({ fileId: uploadedFile.id, environmentId });
      setPreviewState({ fileId: uploadedFile.id, preview });
      setRows(buildImportRows(preview.items, canEditSecrets));
      setStep("preview");
    } catch (error) {
      if (!(error instanceof UploadCanceledError)) {
        setErrorMessage(translateError(error));
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
    commitImport.mutate({
      fileId: previewState.fileId,
      environmentId,
      items: rows
        .filter((row) => row.isIncluded)
        .map((row) => {
          return { key: row.key, kind: row.kind };
        }),
    });
  };

  const hasIncludedRows = rows.some((row) => row.isIncluded);

  return (
    <DSModal
      isOpened
      onClose={handleClose}
      title={t("import.title")}
      isCloseDisabled={isBusy}
      action={
        step === "preview"
          ? {
              label: t("actions.commit"),
              icon: "upload",
              isLoading: commitImport.isPending,
              isDisabled: !hasIncludedRows,
              onClick: handleCommit,
            }
          : undefined
      }
    >
      {step === "file" || previewState === null ? (
        <ImportFileStep
          scopeId={scopeId}
          scopeOptions={scopeOptions}
          onScopeChange={setScopeId}
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
          scopeName={scopeName}
          canEditSecrets={canEditSecrets}
          isBusy={isBusy}
          errorMessage={errorMessage}
          onRowsChange={setRows}
          onBack={handleBack}
        />
      )}
    </DSModal>
  );
};
