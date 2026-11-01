"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TEST_STATUS_COLORS } from "../../typing/constants/story.constant";
import type { TestStatus } from "../../typing/types/story.type";

interface Props {
  status: TestStatus;
}

export const StoryTestStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("stories");

  return (
    <DSBadge color={TEST_STATUS_COLORS[status]} hasDot>
      {t(`testStatuses.${status}`)}
    </DSBadge>
  );
};
