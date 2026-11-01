"use client";

import {
  DSButton,
  DSEmptyState,
  DSErrorState,
  DSSegmentedControl,
  DSStack,
  type DSSegmentedOption,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useHasProjectCapability } from "@/components/project-context/hooks/use-has-project-capability";
import { useCurrentUser } from "@/components/session-guard/hooks/use-current-user";
import { useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetStoryGaps } from "../../hooks/queries/use-get-story-gaps";
import { GAP_STATUS_FILTERS } from "../../typing/constants/gap.constant";
import type { Gap, GapStatusFilter } from "../../typing/types/gap.type";
import { countGapsByFilter, filterGapsByStatus } from "../../utils/gap-filter.util";
import { canReopenGap } from "../../utils/gap-permission.util";
import { GapListSkeleton } from "../gap-list-skeleton/gap-list-skeleton";
import { GapList } from "../gap-list/gap-list";
import { OpenGapsBanner } from "../open-gaps-banner/open-gaps-banner";
import { RaiseGapModal } from "../raise-gap-modal/raise-gap-modal";
import styles from "./story-gaps.module.scss";

interface Props {
  jiraKey: string;
}

export const StoryGaps: FC<Props> = ({ jiraKey }) => {
  const { t } = useTranslation("gaps");
  const project = useCurrentProject();
  const currentUser = useCurrentUser();
  const canRaise = useHasProjectCapability("gap.raise");
  const canAnswer = useHasProjectCapability("gap.answer");
  const canReassign = useHasProjectCapability("gap.reassign");
  const [filter, setFilter] = useState<GapStatusFilter>("open");
  const [isRaiseOpened, setIsRaiseOpened] = useState(false);
  const { data, isPending, isError, isFetching, refetch } = useGetStoryGaps(project.key, jiraKey);
  const counts = countGapsByFilter(data ?? []);
  const filterOptions = GAP_STATUS_FILTERS.map(
    (statusFilter): DSSegmentedOption<GapStatusFilter> => {
      return {
        value: statusFilter,
        label: t(`filter.${statusFilter}`, { count: counts[statusFilter] }),
      };
    },
  );

  const checkCanReopen = (gap: Gap): boolean => {
    return canReopenGap(gap, currentUser.id, project.myRole, canRaise);
  };

  const renderGaps = (): ReactNode => {
    if (isPending) {
      return <GapListSkeleton />;
    }

    if (isError || data === undefined) {
      return (
        <DSErrorState
          title={t("loadError")}
          retryLabel={t("retry")}
          isRetrying={isFetching}
          onRetry={() => {
            void refetch();
          }}
        />
      );
    }

    const visibleGaps = filterGapsByStatus(data, filter);

    if (visibleGaps.length === 0 && filter === "open") {
      return (
        <DSEmptyState
          title={t("empty.openTitle")}
          description={t("empty.openDescription")}
          icon="circleCheck"
        />
      );
    }

    if (visibleGaps.length === 0) {
      return (
        <DSEmptyState
          title={filter === "resolved" ? t("empty.resolvedTitle") : t("empty.allTitle")}
          icon="inbox"
        />
      );
    }

    return (
      <GapList
        gaps={visibleGaps}
        isInboxContext={false}
        canAnswer={canAnswer}
        canReassign={canReassign}
        checkCanReopen={checkCanReopen}
      />
    );
  };

  return (
    <DSStack gap={4} className={styles.root}>
      <OpenGapsBanner projectKey={project.key} jiraKey={jiraKey} />
      <div className={styles.toolbar}>
        <div className={styles.filter}>
          <DSSegmentedControl<GapStatusFilter>
            value={filter}
            options={filterOptions}
            onChange={setFilter}
            ariaLabel={t("filter.label")}
          />
        </div>
        {canRaise && (
          <DSButton
            type="primary"
            icon="plus"
            onClick={() => {
              setIsRaiseOpened(true);
            }}
          >
            {t("actions.raise")}
          </DSButton>
        )}
      </div>
      {renderGaps()}
      {isRaiseOpened && (
        <RaiseGapModal
          projectKey={project.key}
          jiraKey={jiraKey}
          onClose={() => {
            setIsRaiseOpened(false);
          }}
        />
      )}
    </DSStack>
  );
};
