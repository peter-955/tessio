"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export const useFailureApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("failures");

  return useMemo((): ApiErrorMessages => {
    return {
      INVALID_STATUS_TRANSITION: t("errors.changedMeanwhile"),
      ASSIGNEE_NOT_ACTIVE_MEMBER: t("errors.assigneeNotActive"),
    };
  }, [t]);
};
