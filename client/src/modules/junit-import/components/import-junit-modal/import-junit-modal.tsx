"use client";

import {
  DSAlert,
  DSDropzone,
  DSModal,
  DSSelect,
  DSSkeleton,
  DSStack,
  DSText,
  type DSSelectOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { buildRunPath } from "@/modules/runs/utils/run-path.util";
import { useGetSuites } from "@/modules/suites/hooks/queries/use-get-suites";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import { useRouter } from "next/navigation";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePostJunitImport } from "../../hooks/mutations/use-post-junit-import";
import {
  JUNIT_FILE_ERROR_KEYS,
  JUNIT_IMPORT_SKELETON_LINE_COUNT,
} from "../../typing/constants/junit-import.constant";
import type { JunitImport } from "../../typing/types/junit-import.type";
import { findJunitFileError } from "../../utils/junit-file.util";
import { JunitImportResult } from "../junit-import-result/junit-import-result";

interface Props {
  onClose: () => void;
}

export const ImportJunitModal: FC<Props> = ({ onClose }) => {
  const { t } = useTranslation("junitImport");
  const project = useCurrentProject();
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const environments = useGetEnvironments(project.key);
  const suites = useGetSuites(project.key);
  const [chosenEnvironmentId, setChosenEnvironmentId] = useState<string | null>(null);
  const [suiteId, setSuiteId] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [isEnvironmentMissing, setIsEnvironmentMissing] = useState(false);
  const [result, setResult] = useState<JunitImport | null>(null);
  const importJunit = usePostJunitImport(project.key, {
    isGlobalErrorToastDisabled: true,
    onSuccess: (response) => {
      setResult(response);
    },
  });

  const activeEnvironments = environments.data ?? [];
  const defaultEnvironmentId =
    activeEnvironments.find((environment) => {
      return environment.id === project.defaultEnvironmentId;
    })?.id ?? (activeEnvironments.length === 1 ? activeEnvironments[0].id : null);
  const environmentId = chosenEnvironmentId ?? defaultEnvironmentId;
  const environmentOptions: DSSelectOption<string>[] = activeEnvironments.map((environment) => {
    return { value: environment.id, label: environment.name };
  });
  const suiteOptions: DSSelectOption<string>[] = (suites.data ?? []).map((suite) => {
    return { value: suite.id, label: suite.name };
  });
  const serverError = importJunit.error
    ? resolveMessage(importJunit.error, {
        FILE_TOO_LARGE: t("errors.tooLarge"),
        UNKNOWN_REFERENCE: t("errors.unknownReference"),
        NOT_FOUND: t("errors.unknownReference"),
      })
    : null;

  const handleDrop = (files: File[]): void => {
    const [droppedFile] = files;
    if (droppedFile === undefined) {
      return;
    }

    const error = findJunitFileError(droppedFile);
    importJunit.reset();
    setFileError(error === null ? null : t(JUNIT_FILE_ERROR_KEYS[error]));
    setFile(error === null ? droppedFile : null);
  };

  const handleImport = (): void => {
    if (file === null) {
      setFileError(t("errors.fileRequired"));
    }

    setIsEnvironmentMissing(environmentId === null);
    if (file === null || environmentId === null) {
      return;
    }

    importJunit.mutate({ file, environment: environmentId, suite: suiteId });
  };

  const handleOpenRun = (): void => {
    if (result !== null) {
      router.push(buildRunPath(project.key, result.runId));
    }
  };

  if (result !== null) {
    return (
      <DSModal
        isOpened
        onClose={onClose}
        title={t("result.heading")}
        cancelLabel={t("actions.close")}
        action={{ label: t("actions.openRun"), icon: "arrowRight", onClick: handleOpenRun }}
      >
        <JunitImportResult result={result} />
      </DSModal>
    );
  }

  const renderForm = (): ReactNode => {
    if (environments.isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("form.loading")}>
          <DSSkeleton lineCount={JUNIT_IMPORT_SKELETON_LINE_COUNT} />
        </div>
      );
    }

    if (environments.isError) {
      return <DSAlert color="danger">{t("errors.environmentsLoadFailed")}</DSAlert>;
    }

    if (activeEnvironments.length === 0) {
      return <DSAlert color="warning">{t("form.noEnvironment")}</DSAlert>;
    }

    return (
      <DSStack gap={4}>
        <DSText size="sm" color="muted">
          {t("form.description")}
        </DSText>
        {serverError !== null && <DSAlert color="danger">{serverError}</DSAlert>}
        <DSSelect
          label={t("form.environment")}
          placeholder={t("form.environmentPlaceholder")}
          value={environmentId}
          options={environmentOptions}
          onChange={(value) => {
            setChosenEnvironmentId(value);
            setIsEnvironmentMissing(false);
          }}
          error={isEnvironmentMissing ? t("errors.environmentRequired") : undefined}
          isRequired
        />
        <DSSelect
          label={t("form.suite")}
          placeholder={t("form.suitePlaceholder")}
          description={suites.isError ? t("errors.suitesLoadFailed") : t("form.suiteDescription")}
          value={suiteId}
          options={suiteOptions}
          onChange={setSuiteId}
          nothingFoundLabel={t("form.suiteNotFound")}
          isDisabled={suites.isPending || suites.isError}
          isClearable
          isSearchable
        />
        <DSStack gap={2}>
          <DSDropzone
            title={t("form.dropTitle")}
            description={t("form.dropDescription")}
            onDrop={handleDrop}
            isMultiple={false}
            isLoading={importJunit.isPending}
          />
          {file !== null && (
            <DSText size="sm" weight="medium">
              {t("form.chosenFile", { name: file.name })}
            </DSText>
          )}
          {fileError !== null && (
            <DSText size="sm" color="danger" component="span">
              {fileError}
            </DSText>
          )}
        </DSStack>
      </DSStack>
    );
  };

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t("form.title")}
      isCloseDisabled={importJunit.isPending}
      action={{
        label: t("actions.import"),
        icon: "import",
        isLoading: importJunit.isPending,
        isDisabled: activeEnvironments.length === 0,
        onClick: handleImport,
      }}
    >
      {renderForm()}
    </DSModal>
  );
};
