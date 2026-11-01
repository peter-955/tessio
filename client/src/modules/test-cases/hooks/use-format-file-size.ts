"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";

const BYTES_PER_KILOBYTE = 1024;

const BYTES_PER_MEGABYTE = 1048576;

export const useFormatFileSize = (): ((size: number | null) => string) => {
  const { i18n } = useTranslation();

  return useCallback(
    (size: number | null): string => {
      if (size === null) {
        return "";
      }

      if (size < BYTES_PER_KILOBYTE) {
        return new Intl.NumberFormat(i18n.language, { style: "unit", unit: "byte" }).format(size);
      }

      const isMegabytes = size >= BYTES_PER_MEGABYTE;

      return new Intl.NumberFormat(i18n.language, {
        style: "unit",
        unit: isMegabytes ? "megabyte" : "kilobyte",
        maximumFractionDigits: 1,
      }).format(size / (isMegabytes ? BYTES_PER_MEGABYTE : BYTES_PER_KILOBYTE));
    },
    [i18n.language],
  );
};
