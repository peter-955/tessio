"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLAN_STATUS_COLORS } from "../../typing/constants/plan.constant";
import type { PlanStatus } from "../../typing/types/plan.type";

interface Props {
  status: PlanStatus;
}

export const PlanStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("plans");

  return (
    <DSBadge color={PLAN_STATUS_COLORS[status]} hasDot>
      {t(`status.${status}`)}
    </DSBadge>
  );
};
