"use client";

import { DSButton, DSGroup } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { checkHasProjectCapability } from "@/components/project-context/utils/project-capability.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { usePostSync } from "../../hooks/mutations/use-post-sync";
import { useGetSyncStatus } from "../../hooks/queries/use-get-sync-status";
import { useRefreshAfterSync } from "../../hooks/use-refresh-after-sync";
import { MISSING_SYNC_DATE } from "../../typing/constants/sync.constant";
import type { ProjectSyncState } from "../../typing/types/story.type";
import { checkIsSyncInProgress, checkIsSyncStale } from "../../utils/sync-status.util";
import styles from "./sync-control.module.scss";

export const SyncControl: FC = () => {
  const { t } = useTranslation("stories");
  const { t: translateErrors } = useTranslation("errors");
  const formatDate = useFormatDate();
  const project = useCurrentProject();
  const canSync = checkHasProjectCapability(project, "jira.sync");
  const { data, isError, dataUpdatedAt } = useGetSyncStatus(project.key);
  const postSync = usePostSync(project.key);
  useRefreshAfterSync(data?.status);
  const checkedAt = new Date(dataUpdatedAt);
  const isInProgress = checkIsSyncInProgress(data, checkedAt);

  const formatOptionalDate = (isoDate: string | null): string => {
    return isoDate === null ? MISSING_SYNC_DATE : formatDate(isoDate);
  };

  const renderFailure = (state: ProjectSyncState): ReactNode => {
    const reason =
      state.errorCode === null
        ? translateErrors("unexpected")
        : translateErrors(`api.${state.errorCode}`, {
            defaultValue: translateErrors("unexpected"),
          });

    return (
      <>
        <span className={styles.danger}>{t("sync.failed", { reason })}</span>
        {state.lastSucceededAt !== null && (
          <span>{t("sync.lastSucceeded", { date: formatDate(state.lastSucceededAt) })}</span>
        )}
      </>
    );
  };

  const renderStatus = (): ReactNode => {
    if (isError) {
      return <span>{t("sync.unavailable")}</span>;
    }

    if (data === undefined) {
      return null;
    }

    if (checkIsSyncStale(data, checkedAt)) {
      return <span>{t("sync.stale")}</span>;
    }

    switch (data.status) {
      case "never":
        return <span>{t("sync.never")}</span>;
      case "queued":
        return <span>{t("sync.queued")}</span>;
      case "running":
        return <span>{t("sync.running")}</span>;
      case "succeeded":
        return <span>{t("sync.succeeded", { date: formatOptionalDate(data.finishedAt) })}</span>;
      case "failed":
        return renderFailure(data);
    }
  };

  return (
    <DSGroup gap={3} className={styles.control}>
      <div role="status" className={styles.status}>
        {renderStatus()}
      </div>
      {canSync && (
        <DSButton
          type="default"
          icon="refresh"
          isLoading={postSync.isPending || isInProgress}
          onClick={() => {
            postSync.mutate();
          }}
        >
          {t("sync.action")}
        </DSButton>
      )}
    </DSGroup>
  );
};
