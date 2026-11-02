"use client";

import {
  DSCard,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
  DSText,
} from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { LOADING_LINE_COUNT } from "../../typing/constants/insights.constant";
import type { InsightQueryState } from "../../typing/types/insight-query-state.type";

interface Props {
  title: string;
  description?: string;
  state: InsightQueryState;
  isEmpty: boolean;
  emptyTitle: string;
  emptyDescription?: string;
  renderContent: () => ReactNode;
}

export const InsightPanel: FC<Props> = ({
  title,
  description,
  state,
  isEmpty,
  emptyTitle,
  emptyDescription,
  renderContent,
}) => {
  const { t } = useTranslation("insights");

  const renderBody = (): ReactNode => {
    if (state.isPending) {
      return (
        <div aria-busy="true" aria-label={t("loading", { title })}>
          <DSSkeleton lineCount={LOADING_LINE_COUNT} />
        </div>
      );
    }

    if (state.isError) {
      return (
        <DSErrorState
          title={t("loadError", { title })}
          retryLabel={t("retry")}
          isRetrying={state.isFetching}
          onRetry={() => {
            void state.refetch();
          }}
        />
      );
    }

    if (isEmpty) {
      return (
        <DSEmptyState title={emptyTitle} description={emptyDescription} icon="insights" size="sm" />
      );
    }

    return renderContent();
  };

  return (
    <DSCard title={title}>
      <DSStack gap={3}>
        {description !== undefined && (
          <DSText size="sm" color="muted">
            {description}
          </DSText>
        )}
        {renderBody()}
      </DSStack>
    </DSCard>
  );
};
