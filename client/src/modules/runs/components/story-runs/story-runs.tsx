"use client";

import {
  DSButtonLink,
  DSEmptyState,
  DSErrorState,
  DSGroup,
  DSSkeleton,
  DSStack,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { RunsTable } from "@/components/runs-table/runs-table";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetRuns } from "../../hooks/queries/use-get-runs";
import { LOADING_ROW_COUNT, NOT_FOUND_STATUS } from "../../typing/constants/run.constant";
import { buildRunsPath } from "../../utils/run-path.util";

interface Props {
  jiraKey: string;
  actions?: ReactNode;
}

export const StoryRuns: FC<Props> = ({ jiraKey, actions }) => {
  const { t } = useTranslation("runs");
  const project = useCurrentProject();
  const { data, error, isPending, isError, isFetching, refetch } = useGetRuns(project.key, {
    status: null,
    storyKey: jiraKey,
    suiteId: null,
  });

  const renderRuns = (): ReactNode => {
    if (isPending) {
      return (
        <div role="status" aria-busy="true" aria-label={t("loading")}>
          <DSSkeleton lineCount={LOADING_ROW_COUNT} height={40} />
        </div>
      );
    }

    if (error?.status === NOT_FOUND_STATUS || (data !== undefined && data.length === 0)) {
      return (
        <DSEmptyState
          title={t("empty.storyTitle")}
          description={t("empty.storyDescription")}
          icon="runs"
        />
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

    return <RunsTable runs={data} projectKey={project.key} isStoryColumnShown={false} />;
  };

  return (
    <DSStack gap={4}>
      <DSGroup justify="end" gap={2} isWrapping>
        {actions}
        <DSButtonLink
          href={buildRunsPath(project.key, { storyKey: jiraKey })}
          type="default"
          hasArrow
        >
          {t("empty.viewAll")}
        </DSButtonLink>
      </DSGroup>
      {renderRuns()}
    </DSStack>
  );
};
