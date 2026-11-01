"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { SPRINT_STATE_COLORS } from "../../typing/constants/sprint.constant";
import type { SprintState } from "../../typing/types/sprint.type";

interface Props {
  state: SprintState;
}

export const SprintStateBadge: FC<Props> = ({ state }) => {
  const { t } = useTranslation("sprints");

  return <DSBadge color={SPRINT_STATE_COLORS[state]}>{t(`states.${state}`)}</DSBadge>;
};
