"use client";

import { DSBadge, DSButton, DSDrawer, DSErrorState, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetTestFileVersions } from "../../hooks/queries/use-get-test-file-versions";
import { useFormatFileSize } from "../../hooks/use-format-file-size";
import type { TestFile } from "../../typing/types/test-case.type";
import styles from "./file-versions-drawer.module.scss";

interface Props {
  caseCode: string;
  file: TestFile | null;
  canDownload: boolean;
  onDownload: (storedFileId: string) => void;
  onClose: () => void;
}

export const FileVersionsDrawer: FC<Props> = ({
  caseCode,
  file,
  canDownload,
  onDownload,
  onClose,
}) => {
  const { t } = useTranslation("testCases");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const formatFileSize = useFormatFileSize();
  const fileKey = file?.key ?? "";
  const { data, isPending, isError, isFetching, refetch } = useGetTestFileVersions(
    project.key,
    caseCode,
    fileKey,
    file !== null,
  );

  const renderContent = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={4} />
        </div>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("files.versionsError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    return (
      <ul className={styles.list}>
        {data.map((version) => {
          const isCurrent = version.id === file?.currentVersion.id;

          return (
            <li key={version.id} className={styles.item}>
              <div className={styles.meta}>
                <span className={styles.fileName}>
                  {t("files.versionNumber", { number: version.number })} · {version.fileName}
                </span>
                <span className={styles.muted}>
                  {formatFileSize(version.size)} · {formatDate(version.createdAt)}
                </span>
                {isCurrent && <DSBadge color="tessio">{t("history.current")}</DSBadge>}
              </div>
              {canDownload && (
                <DSButton
                  type="default"
                  size="sm"
                  onClick={() => {
                    onDownload(version.storedFileId);
                  }}
                >
                  {t("actions.download")}{" "}
                  <span className={styles.visuallyHidden}>
                    {t("files.versionNumber", { number: version.number })}
                  </span>
                </DSButton>
              )}
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <DSDrawer
      isOpened={file !== null}
      onClose={onClose}
      title={t("files.versionsTitle", { key: fileKey })}
      closeLabel={t("actions.close")}
    >
      {file !== null && renderContent()}
    </DSDrawer>
  );
};
