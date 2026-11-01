"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export const useGapApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("gaps");

  return useMemo((): ApiErrorMessages => {
    return {
      GAP_NOT_OPEN: t("errors.alreadyResolved"),
      INVALID_STATUS_TRANSITION: t("errors.alreadyOpen"),
      UNKNOWN_REFERENCE: t("errors.unknownTarget"),
      ASSIGNEE_NOT_ACTIVE_MEMBER: t("errors.assigneeNotActive"),
    };
  }, [t]);
};
