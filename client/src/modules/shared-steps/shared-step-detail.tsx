"use client";

import { DSErrorState, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { SharedStepDetailView } from "./components/shared-step-detail-view/shared-step-detail-view";
import { SharedStepNotFound } from "./components/shared-step-not-found/shared-step-not-found";
import { useGetSharedStep } from "./hooks/queries/use-get-shared-step";
import {
  LOADING_LINE_COUNT,
  NOT_FOUND_STATUS,
  SHARED_STEP_KEY_PATTERN,
} from "./typing/constants/shared-step.constant";
import { normalizeSharedStepKey } from "./utils/shared-step-form.util";

interface Props {
  sharedStepKey: string;
}

export const SharedStepDetailPage: FC<Props> = ({ sharedStepKey }) => {
  const { t } = useTranslation("sharedSteps");
  const project = useCurrentProject();
  const normalizedKey = normalizeSharedStepKey(sharedStepKey);
  const isValidKey = SHARED_STEP_KEY_PATTERN.test(normalizedKey);
  const { data, error, isPending, isError, isFetching, refetch } = useGetSharedStep(
    project.key,
    normalizedKey,
    isValidKey,
  );

  if (!isValidKey || error?.status === NOT_FOUND_STATUS) {
    return <SharedStepNotFound projectKey={project.key} />;
  }

  if (isPending) {
    return (
      <div role="status" aria-busy="true" aria-label={t("detail.loading")}>
        <DSSkeleton lineCount={LOADING_LINE_COUNT} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("detail.loadError")}
        retryLabel={t("detail.retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  return <SharedStepDetailView key={data.id} sharedStep={data} />;
};
