"use client";

import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { formatRelativeTime } from "../utils/relative-time.util";

export const useFormatRelativeTime = (): ((isoDate: string) => string) => {
  const { i18n } = useTranslation();
  const formatDate = useFormatDate();

  return useCallback(
    (isoDate: string): string => {
      return formatRelativeTime(isoDate, new Date(), i18n.language) ?? formatDate(isoDate);
    },
    [formatDate, i18n.language],
  );
};
