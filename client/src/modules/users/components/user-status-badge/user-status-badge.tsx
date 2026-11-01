"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { USER_STATUS_BADGE_COLORS } from "../../typing/constants/user.constant";
import type { UserStatus } from "../../typing/types/workspace-user.type";

interface Props {
  status: UserStatus;
}

export const UserStatusBadge: FC<Props> = ({ status }) => {
  const { t } = useTranslation("users");

  return <DSBadge color={USER_STATUS_BADGE_COLORS[status]}>{t(`statuses.${status}`)}</DSBadge>;
};
