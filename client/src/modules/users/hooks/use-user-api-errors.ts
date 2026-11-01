"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export const useUserApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("users");

  return useMemo((): ApiErrorMessages => {
    return {
      CANNOT_CHANGE_OWN_OR_OWNER: t("errors.cannotChange"),
      OWNER_ONLY: t("errors.ownerOnly"),
      USER_NOT_INVITED: t("errors.notInvited"),
    };
  }, [t]);
};
