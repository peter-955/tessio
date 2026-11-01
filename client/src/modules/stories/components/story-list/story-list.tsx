"use client";

import { DSEmptyState, DSErrorState, DSSkeleton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetStories } from "../../hooks/queries/use-get-stories";
import { useGetStoryProgress } from "../../hooks/queries/use-get-story-progress";
import type { StoryFilters } from "../../typing/types/story-filters.type";
import { checkHasStoryFilters } from "../../utils/story-filters.util";
import { mapStoryProgressById } from "../../utils/story-progress.util";
import { StoryTable } from "../story-table/story-table";

interface Props {
  projectKey: string;
  filters: StoryFilters;
  isSprintColumnShown: boolean;
}

export const StoryList: FC<Props> = ({ projectKey, filters, isSprintColumnShown }) => {
  const { t } = useTranslation("stories");
  const { data, isPending, isError, isFetching, refetch } = useGetStories(projectKey, filters);
  const progress = useGetStoryProgress(projectKey, filters.sprintId);
  const progressByStoryId =
    progress.isError || progress.data === undefined
      ? undefined
      : mapStoryProgressById(progress.data);

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
        title={t("loadError")}
        retryLabel={t("retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  if (data.length === 0) {
    if (checkHasStoryFilters(filters, !isSprintColumnShown)) {
      return (
        <DSEmptyState
          title={t("emptyFiltered.title")}
          description={t("emptyFiltered.description")}
          icon="search"
        />
      );
    }

    return (
      <DSEmptyState title={t("empty.title")} description={t("empty.description")} icon="stories" />
    );
  }

  return (
    <StoryTable
      projectKey={projectKey}
      stories={data}
      isSprintColumnShown={isSprintColumnShown}
      progressByStoryId={progressByStoryId}
    />
  );
};
