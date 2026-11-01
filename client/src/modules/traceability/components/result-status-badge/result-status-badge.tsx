"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { RESULT_STATUS_COLORS } from "../../typing/constants/traceability.constant";
import type { LatestResult } from "../../typing/types/traceability.type";

interface Props {
  result: LatestResult | null;
}

export const ResultStatusBadge: FC<Props> = ({ result }) => {
  const { t } = useTranslation("traceability");
  const status = result?.status ?? "not_run";

  return (
    <DSBadge color={RESULT_STATUS_COLORS[status]} hasDot>
      {t(`resultStatus.${status}`)}
    </DSBadge>
  );
};
