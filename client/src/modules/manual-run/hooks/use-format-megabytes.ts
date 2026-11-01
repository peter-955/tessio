"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { BYTES_PER_MEGABYTE } from "../typing/constants/manual-run.constant";

export const useFormatMegabytes = (): ((sizeInBytes: number) => string) => {
  const { i18n } = useTranslation();

  return useCallback(
    (sizeInBytes: number): string => {
      return new Intl.NumberFormat(i18n.language, {
        style: "unit",
        unit: "megabyte",
        maximumFractionDigits: 1,
      }).format(sizeInBytes / BYTES_PER_MEGABYTE);
    },
    [i18n.language],
  );
};
