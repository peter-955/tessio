"use client";

import { DSAlert } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetStoryGaps } from "../../hooks/queries/use-get-story-gaps";
import { countOpenGaps } from "../../utils/gap-filter.util";

interface Props {
  projectKey: string;
  jiraKey: string;
}

export const OpenGapsBanner: FC<Props> = ({ projectKey, jiraKey }) => {
  const { t } = useTranslation("gaps");
  const { data } = useGetStoryGaps(projectKey, jiraKey);
  const openCount = data === undefined ? 0 : countOpenGaps(data);

  if (openCount === 0) {
    return null;
  }

  return (
    <DSAlert color="warning" title={t("banner.title", { count: openCount })}>
      {t("banner.description")}
    </DSAlert>
  );
};
