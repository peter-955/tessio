"use client";

import {
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSPageHeader,
  DSSkeleton,
  DSTitle,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { StoryFilters } from "@/modules/stories/components/story-filters/story-filters";
import { StoryList } from "@/modules/stories/components/story-list/story-list";
import { SyncControl } from "@/modules/stories/components/sync-control/sync-control";
import type { StoryFilters as StoryFilterValues } from "@/modules/stories/typing/types/story-filters.type";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { SprintDates } from "./components/sprint-dates/sprint-dates";
import { SprintStateBadge } from "./components/sprint-state-badge/sprint-state-badge";
import { useGetSprint } from "./hooks/queries/use-get-sprint";
import styles from "./sprint-detail.module.scss";
import { NOT_FOUND_STATUSES, UUID_PATTERN } from "./typing/constants/sprint.constant";
import { buildSprintsPath } from "./utils/sprint-path.util";

interface Props {
  sprintId: string;
}

export const SprintDetailPage: FC<Props> = ({ sprintId }) => {
  const { t } = useTranslation("sprints");
  const project = useCurrentProject();
  const isValidSprintId = UUID_PATTERN.test(sprintId);
  const [filters, setFilters] = useState<StoryFilterValues>({
    sprintId,
    testStatus: null,
    query: "",
  });
  const { data, error, isPending, isError, isFetching, refetch } = useGetSprint(
    project.key,
    sprintId,
    isValidSprintId,
  );

  if (!isValidSprintId || (error !== null && NOT_FOUND_STATUSES.includes(error.status))) {
    return (
      <DSEmptyState
        title={t("detail.notFound.title")}
        description={t("detail.notFound.description")}
        icon="sprints"
        action={
          <DSButtonLink href={buildSprintsPath(project.key)} type="default">
            {t("detail.back")}
          </DSButtonLink>
        }
      />
    );
  }

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={6} />
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

  return (
    <>
      <div className={styles.back}>
        <DSButtonLink href={buildSprintsPath(project.key)} type="ghost">
          {t("detail.back")}
        </DSButtonLink>
      </div>
      <DSPageHeader
        title={data.name}
        description={
          <span className={styles.details}>
            <SprintStateBadge state={data.state} />
            <SprintDates sprint={data} />
          </span>
        }
        actions={<SyncControl />}
      />
      <DSTitle order={2} type="section" className={styles.sectionTitle}>
        {t("detail.storiesTitle")}
      </DSTitle>
      <StoryFilters
        filters={filters}
        onChange={(nextFilters) => {
          setFilters({ ...nextFilters, sprintId });
        }}
        isSprintFilterShown={false}
        sprints={[]}
      />
      <StoryList projectKey={project.key} filters={filters} isSprintColumnShown={false} />
    </>
  );
};
