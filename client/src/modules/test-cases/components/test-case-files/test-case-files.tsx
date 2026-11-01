"use client";

import {
  DSButton,
  DSCopyButton,
  DSEmptyState,
  DSTable,
  DSTooltip,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useDownloadFile } from "../../hooks/use-download-file";
import { useFormatFileSize } from "../../hooks/use-format-file-size";
import type { TestCaseDetail, TestFile } from "../../typing/types/test-case.type";
import { buildFileReference } from "../../utils/file-reference.util";
import { AttachFileModal } from "../attach-file-modal/attach-file-modal";
import { FileVersionsDrawer } from "../file-versions-drawer/file-versions-drawer";
import styles from "./test-case-files.module.scss";

interface Props {
  detail: TestCaseDetail;
  canAttach: boolean;
  hasUnsavedChanges: boolean;
}

interface AttachState {
  file: TestFile | null;
}

export const TestCaseFiles: FC<Props> = ({ detail, canAttach, hasUnsavedChanges }) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const formatFileSize = useFormatFileSize();
  const canDownload = checkHasProjectCapability(project, "file.download");
  const downloadFile = useDownloadFile(project.key);
  const [attachState, setAttachState] = useState<AttachState | null>(null);
  const [versionsFile, setVersionsFile] = useState<TestFile | null>(null);
  const saveFirstTitle = hasUnsavedChanges ? t("form.saveFirst") : undefined;

  const handleDownload = (storedFileId: string): void => {
    downloadFile.mutate(storedFileId);
  };

  return (
    <div className={styles.files}>
      {canAttach && (
        <div className={styles.toolbar}>
          <DSTooltip label={t("form.saveFirst")} isDisabled={!hasUnsavedChanges}>
            <span>
              <DSButton
                type="primary"
                icon="plus"
                isDisabled={hasUnsavedChanges}
                title={saveFirstTitle}
                onClick={() => {
                  setAttachState({ file: null });
                }}
              >
                {t("actions.addFile")}
              </DSButton>
            </span>
          </DSTooltip>
        </div>
      )}
      {detail.files.length === 0 ? (
        <DSEmptyState title={t("files.empty")} icon="file" size="sm" />
      ) : (
        <DSTable label={t("files.tableLabel")}>
          <caption className={styles.visuallyHidden}>{t("files.tableLabel")}</caption>
          <thead>
            <tr>
              <th scope="col">{t("files.key")}</th>
              <th scope="col">{t("files.fileName")}</th>
              <th scope="col">{t("files.version")}</th>
              <th scope="col">{t("files.size")}</th>
              <th scope="col">{t("files.uploaded")}</th>
              <th scope="col">{t("files.actionsColumn")}</th>
            </tr>
          </thead>
          <tbody>
            {detail.files.map((file) => {
              const { currentVersion } = file;

              return (
                <tr key={file.id}>
                  <th scope="row">
                    <span className={styles.key}>
                      <span>{file.key}</span>
                      <DSCopyButton value={buildFileReference(file.key)} />
                    </span>
                  </th>
                  <td className={styles.fileName} title={currentVersion.fileName}>
                    {currentVersion.fileName}
                  </td>
                  <td>{t("files.versionNumber", { number: currentVersion.number })}</td>
                  <td>{formatFileSize(currentVersion.size)}</td>
                  <td>{formatDate(currentVersion.createdAt)}</td>
                  <td>
                    <span className={styles.actions}>
                      {canDownload && (
                        <DSButton
                          type="default"
                          size="sm"
                          isLoading={
                            downloadFile.isPending &&
                            downloadFile.variables === currentVersion.storedFileId
                          }
                          onClick={() => {
                            handleDownload(currentVersion.storedFileId);
                          }}
                        >
                          {t("actions.download")}{" "}
                          <span className={styles.visuallyHidden}>{file.key}</span>
                        </DSButton>
                      )}
                      {canAttach && (
                        <DSButton
                          type="default"
                          size="sm"
                          icon="upload"
                          isDisabled={hasUnsavedChanges}
                          title={saveFirstTitle}
                          onClick={() => {
                            setAttachState({ file });
                          }}
                        >
                          {t("actions.newVersion")}{" "}
                          <span className={styles.visuallyHidden}>{file.key}</span>
                        </DSButton>
                      )}
                      <DSButton
                        type="ghost"
                        size="sm"
                        onClick={() => {
                          setVersionsFile(file);
                        }}
                      >
                        {t("actions.versions")}{" "}
                        <span className={styles.visuallyHidden}>{file.key}</span>
                      </DSButton>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      )}
      {attachState !== null && (
        <AttachFileModal
          detail={detail}
          existingFile={attachState.file}
          onClose={() => {
            setAttachState(null);
          }}
        />
      )}
      <FileVersionsDrawer
        caseCode={detail.code}
        file={versionsFile}
        canDownload={canDownload}
        onDownload={handleDownload}
        onClose={() => {
          setVersionsFile(null);
        }}
      />
    </div>
  );
};
