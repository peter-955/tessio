import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { splitDuration } from "../utils/format.util";

export const useFormatDuration = (): ((durationInMilliseconds: number) => string) => {
  const { t } = useTranslation("common");

  return useCallback(
    (durationInMilliseconds: number): string => {
      if (durationInMilliseconds === 0) {
        return "—";
      }

      const { minutes, seconds } = splitDuration(durationInMilliseconds);

      if (minutes === 0) {
        return t("duration.seconds", { seconds });
      }

      return t("duration.minutesSeconds", { minutes, seconds });
    },
    [t],
  );
};
