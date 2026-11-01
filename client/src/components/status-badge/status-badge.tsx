"use client";

import { DSBadge } from "@/components/design-system";
import { TEST_STATUS_COLORS } from "@/shared/typing/constants/test-status.constant";
import type { TestOutcome } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  status: TestOutcome;
}

export const StatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("runs");

  return (
    <DSBadge color={TEST_STATUS_COLORS[status]} hasDot>
      {t(`status.${status}`)}
    </DSBadge>
  );
};
