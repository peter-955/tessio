"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { FAILURE_STATUS_COLORS } from "../../typing/constants/failure.constant";
import type { FailureStatus } from "../../typing/types/failure.type";

interface Props {
  status: FailureStatus;
}

export const FailureStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("failures");

  return (
    <DSBadge color={FAILURE_STATUS_COLORS[status]} hasDot>
      {t(`status.${status}`)}
    </DSBadge>
  );
};
