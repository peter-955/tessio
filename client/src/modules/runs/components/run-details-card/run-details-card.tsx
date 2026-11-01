"use client";

import { DSCard, DSText } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useFormatDuration } from "@/shared/hooks/use-format-duration";
import type { RunDetail } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { computeRunDuration } from "../../utils/run-duration.util";
import styles from "./run-details-card.module.scss";
import { RunLineage } from "./run-lineage/run-lineage";

interface Props {
  projectKey: string;
  run: RunDetail;
}

export const RunDetailsCard: FC<Props> = ({ projectKey, run }) => {
  const { t } = useTranslation("runs");
  const formatDate = useFormatDate();
  const formatDuration = useFormatDuration();
  const duration = computeRunDuration(run.startedAt, run.finishedAt);

  return (
    <DSCard title={t("detail.details")}>
      <dl className={styles.list}>
        <div className={styles.row}>
          <dt>{t("table.status")}</dt>
          <dd className={styles.status}>
            <StatusBadge status={run.status} />
            {run.status === "aborted" && run.abortReason !== null && (
              <DSText size="xs" color="muted" component="span">
                {t(`abortReason.${run.abortReason}`)}
              </DSText>
            )}
          </dd>
        </div>
        <div className={styles.row}>
          <dt>{t("table.executor")}</dt>
          <dd>{t(`executor.${run.executor}`)}</dd>
        </div>
        <div className={styles.row}>
          <dt>{t("table.environment")}</dt>
          <dd>{run.environmentName}</dd>
        </div>
        <div className={styles.row}>
          <dt>{t("table.startedBy")}</dt>
          <dd>{run.startedByName}</dd>
        </div>
        <div className={styles.row}>
          <dt>{t("detail.startedAt")}</dt>
          <dd>{formatDate(run.startedAt)}</dd>
        </div>
        {run.finishedAt !== null && (
          <div className={styles.row}>
            <dt>{t("detail.finishedAt")}</dt>
            <dd>{formatDate(run.finishedAt)}</dd>
          </div>
        )}
        <div className={styles.row}>
          <dt>{t("table.duration")}</dt>
          <dd>{duration === null ? t("table.running") : formatDuration(duration)}</dd>
        </div>
      </dl>
      <RunLineage
        projectKey={projectKey}
        parentRunId={run.parentRunId}
        childRunIds={run.childRunIds}
      />
    </DSCard>
  );
};
