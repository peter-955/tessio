"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";

export const useFormatDay = (): ((value: string | number) => string) => {
  const { i18n } = useTranslation();

  return useCallback(
    (value: string | number): string => {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return "";
      }

      return new Intl.DateTimeFormat(i18n.language, {
        dateStyle: "medium",
        timeZone: "UTC",
      }).format(date);
    },
    [i18n.language],
  );
};
