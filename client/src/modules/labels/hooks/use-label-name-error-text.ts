"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { MAX_LABEL_NAME_LENGTH } from "../typing/constants/label.constant";
import type { LabelNameError } from "../typing/types/label-name-error.type";

export const useLabelNameErrorText = (): ((error: LabelNameError | null) => string | null) => {
  const { t } = useTranslation("labels");

  return useCallback(
    (error: LabelNameError | null): string | null => {
      if (error === null) {
        return null;
      }

      return error === "tooLong"
        ? t("validation.tooLong", { max: MAX_LABEL_NAME_LENGTH })
        : t(`validation.${error}`);
    },
    [t],
  );
};
