"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { MAX_SUITE_CASES } from "../typing/constants/suite.constant";

export const useSuiteApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("suites");

  return useMemo((): ApiErrorMessages => {
    return {
      SUITE_NAME_ALREADY_USED: t("errors.nameAlreadyUsed"),
      SUITE_ARCHIVED: t("errors.archived"),
      UNKNOWN_REFERENCE: t("errors.unknownReference"),
      INVALID_REQUEST: t("errors.invalidRequest", { max: MAX_SUITE_CASES }),
    };
  }, [t]);
};
