"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export const usePlanApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("plans");

  return useMemo((): ApiErrorMessages => {
    return {
      PLAN_NOT_OPEN: t("errors.notOpen"),
      PLAN_FAILURES_ACTIVE: t("errors.failuresActive"),
      UNKNOWN_REFERENCE: t("errors.unknownReference"),
      INVALID_REQUEST: t("errors.invalidRequest"),
    };
  }, [t]);
};
