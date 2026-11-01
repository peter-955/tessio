import { useCallback } from "react";
import { useTranslation } from "react-i18next";

export const useFormatDate = (): ((isoDate: string) => string) => {
  const { i18n } = useTranslation();

  return useCallback(
    (isoDate: string): string => {
      const formattedDate = new Intl.DateTimeFormat(i18n.language, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      }).format(new Date(isoDate));

      return `${formattedDate} UTC`;
    },
    [i18n.language],
  );
};
