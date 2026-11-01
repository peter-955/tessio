"use client";

import {
  DSAlert,
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { UUID_PATTERN } from "@/modules/sprints/typing/constants/sprint.constant";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { FailedStepCard } from "./components/failed-step-card/failed-step-card";
import { FailureHeader } from "./components/failure-header/failure-header";
import { FailureResultHistory } from "./components/failure-result-history/failure-result-history";
import { FailureTimeline } from "./components/failure-timeline/failure-timeline";
import styles from "./failure-detail.module.scss";
import { useGetFailure } from "./hooks/queries/use-get-failure";
import { NOT_FOUND_STATUS } from "./typing/constants/failure.constant";
import { checkCanAssignFailure } from "./utils/failure-capability.util";
import { buildFailuresPath } from "./utils/failure-path.util";

interface Props {
  failureId: string;
}

export const FailureDetailPage: FC<Props> = ({ failureId }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const isValidId = UUID_PATTERN.test(failureId);
  const { data, error, isPending, isError, isFetching, refetch } = useGetFailure(
    project.key,
    failureId,
  );

  if (!isValidId || error?.status === NOT_FOUND_STATUS) {
    return (
      <DSEmptyState
        title={t("detail.notFoundTitle")}
        description={t("detail.notFoundDescription")}
        icon="failures"
        action={
          <DSButtonLink href={buildFailuresPath(project.key)} type="default">
            {t("detail.back")}
          </DSButtonLink>
        }
      />
    );
  }

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={8} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("detail.loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  const isAssigneeDeactivated =
    data.assigneeStatus === "deactivated" && checkCanAssignFailure(project, data);

  return (
    <>
      <FailureHeader failure={data} />
      {isAssigneeDeactivated && (
        <div className={styles.alert}>
          <DSAlert color="warning">{t("assignee.deactivatedHint")}</DSAlert>
        </div>
      )}
      <div className={styles.grid}>
        <div className={styles.column}>
          <FailedStepCard failure={data} />
          <FailureResultHistory results={data.results} />
        </div>
        <div className={styles.column}>
          <FailureTimeline events={data.events} />
        </div>
      </div>
    </>
  );
};
