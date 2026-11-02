"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export const useSharedStepApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("sharedSteps");

  return useMemo((): ApiErrorMessages => {
    return {
      SHARED_STEP_KEY_ALREADY_USED: t("errors.keyAlreadyUsed"),
      INVALID_STEP_SHAPE: t("errors.invalidStepShape"),
      CONFLICT: t("errors.conflict"),
    };
  }, [t]);
};
