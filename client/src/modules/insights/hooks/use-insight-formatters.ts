"use client";

import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { PERCENT_SCALE } from "../typing/constants/insights.constant";
import { pickDuration } from "../utils/insight-number.util";

const MAXIMUM_FRACTION_DIGITS = 1;

interface Result {
  formatCount: (value: number) => string;
  formatPercent: (value: number) => string;
  formatShare: (share: number | null) => string;
  formatDays: (value: number) => string;
  formatDuration: (seconds: number | null) => string;
  formatTokens: (value: number) => string;
}

export const useInsightFormatters = (): Result => {
  const { t, i18n } = useTranslation("insights");
  const language = i18n.language;
  const noValue = t("noValue");

  return useMemo((): Result => {
    const countFormat = new Intl.NumberFormat(language, {
      maximumFractionDigits: MAXIMUM_FRACTION_DIGITS,
    });
    const percentFormat = new Intl.NumberFormat(language, {
      style: "percent",
      maximumFractionDigits: MAXIMUM_FRACTION_DIGITS,
    });
    const tokenFormat = new Intl.NumberFormat(language, {
      notation: "compact",
      maximumFractionDigits: MAXIMUM_FRACTION_DIGITS,
    });

    const formatUnit = (value: number, unit: string): string => {
      return new Intl.NumberFormat(language, {
        style: "unit",
        unit,
        unitDisplay: "short",
        maximumFractionDigits: MAXIMUM_FRACTION_DIGITS,
      }).format(value);
    };

    return {
      formatCount: (value) => {
        return countFormat.format(value);
      },
      formatPercent: (value) => {
        return percentFormat.format(value / PERCENT_SCALE);
      },
      formatShare: (share) => {
        return share === null ? noValue : percentFormat.format(share);
      },
      formatDays: (value) => {
        return formatUnit(value, "day");
      },
      formatDuration: (seconds) => {
        if (seconds === null) {
          return noValue;
        }
        const duration = pickDuration(seconds);

        return formatUnit(duration.value, duration.unit);
      },
      formatTokens: (value) => {
        return tokenFormat.format(value);
      },
    };
  }, [language, noValue]);
};
