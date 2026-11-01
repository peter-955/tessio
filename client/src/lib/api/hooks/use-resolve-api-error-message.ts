"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { ApiError } from "../api-error";
import type { ApiErrorMessages } from "../typing/types/api-error-messages.type";

export const useResolveApiErrorMessage = (): ((
  error: unknown,
  apiErrors?: ApiErrorMessages,
) => string) => {
  const { t } = useTranslation("errors");

  return useCallback(
    (error: unknown, apiErrors?: ApiErrorMessages): string => {
      if (!(error instanceof ApiError) || error.code === null) {
        return t("unexpected");
      }

      const overrideMessage = apiErrors?.[error.code];
      if (overrideMessage !== undefined) {
        return overrideMessage;
      }

      return t(`api.${error.code}`, { defaultValue: t("unexpected") });
    },
    [t],
  );
};
