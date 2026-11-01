"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { RESULT_STATUS_COLORS } from "../../typing/constants/result-status.constant";
import type { ResultStatus } from "../../typing/types/manual-run.type";

interface Props {
  status: ResultStatus;
}

export const ResultStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("manualRun");

  return <DSBadge color={RESULT_STATUS_COLORS[status]}>{t(`status.${status}`)}</DSBadge>;
};
