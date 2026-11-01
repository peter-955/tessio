"use client";

import {
  DSAlert,
  DSBadge,
  DSButton,
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSText,
  DSTitle,
} from "@/components/design-system";
import { useFormatDay } from "@/modules/stories/hooks/use-format-day";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetDashboard } from "../../hooks/queries/use-get-dashboard";
import {
  MISSING_SPRINT_DATE,
  NOT_FOUND_STATUS,
  SPRINT_STATE_COLORS,
} from "../../typing/constants/dashboard.constant";
import type { DashboardSprint } from "../../typing/types/dashboard.type";
import { buildTestStatusRows } from "../../utils/test-status.util";
import { CoverageMeter } from "../coverage-meter/coverage-meter";
import { SprintPicker } from "../sprint-picker/sprint-picker";
import { SprintStats } from "../sprint-stats/sprint-stats";
import { TestStatusBreakdown } from "../test-status-breakdown/test-status-breakdown";
import styles from "./sprint-panel.module.scss";

interface Props {
  projectKey: string;
  sprintId: string | null;
  onSprintChange: (sprintId: string | null) => void;
}

export const SprintPanel: FC<Props> = ({ projectKey, sprintId, onSprintChange }) => {
  const { t } = useTranslation("dashboard");
  const formatDay = useFormatDay();
  const { data, error, isPending, isError, isFetching, refetch } = useGetDashboard(
    projectKey,
    sprintId,
  );

  const formatSprintDate = (isoDate: string | null): string => {
    return isoDate === null ? MISSING_SPRINT_DATE : formatDay(isoDate);
  };

  const renderSprint = (sprint: DashboardSprint): ReactNode => {
    return (
      <div className={styles.sprint}>
        <DSText weight="medium" component="span" className={styles.sprintName}>
          {sprint.name}
        </DSText>
        <DSBadge color={SPRINT_STATE_COLORS[sprint.state]}>
          {t(`sprint.states.${sprint.state}`)}
        </DSBadge>
        <DSText size="sm" color="muted" component="span">
          {t("sprint.dates", {
            start: formatSprintDate(sprint.startAt),
            end: formatSprintDate(sprint.endAt),
          })}
        </DSText>
      </div>
    );
  };

  const renderBody = (): ReactNode => {
    if (isPending) {
      return (
        <div aria-busy="true">
          <DSSkeleton lineCount={6} />
        </div>
      );
    }

    if (error?.status === NOT_FOUND_STATUS) {
      return (
        <DSAlert
          color="warning"
          title={t("sprint.notFound.title")}
          action={
            <DSButton
              onClick={() => {
                onSprintChange(null);
              }}
            >
              {t("sprint.notFound.reset")}
            </DSButton>
          }
        >
          {t("sprint.notFound.description")}
        </DSAlert>
      );
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("sprint.loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    if (data.sprint === null) {
      return (
        <DSEmptyState
          title={t("sprint.empty.title")}
          description={t("sprint.empty.description")}
          icon="sprints"
        />
      );
    }

    return (
      <div className={styles.body}>
        <div className={styles.fullWidth}>
          <SprintStats projectKey={projectKey} sprintId={data.sprint.id} summary={data} />
        </div>
        <TestStatusBreakdown
          rows={buildTestStatusRows(projectKey, data.sprint.id, data.testStatusCounts)}
        />
        <CoverageMeter coverage={data.coverage} />
      </div>
    );
  };

  return (
    <DSCard>
      <div className={styles.header}>
        <div className={styles.heading}>
          <DSTitle order={2} type="section">
            {t("sprint.title")}
          </DSTitle>
          {data?.sprint && renderSprint(data.sprint)}
        </div>
        <div className={styles.picker}>
          <SprintPicker
            projectKey={projectKey}
            value={sprintId ?? data?.sprint?.id ?? null}
            onChange={onSprintChange}
          />
        </div>
      </div>
      {renderBody()}
    </DSCard>
  );
};
