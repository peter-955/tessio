"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { KNOWN_EXECUTORS } from "../typing/constants/insights.constant";

type KnownExecutor = (typeof KNOWN_EXECUTORS)[number];

const checkIsKnownExecutor = (executor: string): executor is KnownExecutor => {
  return (KNOWN_EXECUTORS as readonly string[]).includes(executor);
};

export const useLabelExecutor = (): ((executor: string) => string) => {
  const { t } = useTranslation("insights");

  return useCallback(
    (executor: string): string => {
      return checkIsKnownExecutor(executor) ? t(`executor.${executor}`) : executor;
    },
    [t],
  );
};
