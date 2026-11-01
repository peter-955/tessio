"use client";

import type { ApiErrorMessages } from "@/lib/api/typing/types/api-error-messages.type";
import { MAX_FILE_SIZE_IN_BYTES } from "@/lib/uploads/typing/constants/upload-limits.constant";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { useFormatMegabytes } from "./use-format-megabytes";

export const useManualRunApiErrors = (): ApiErrorMessages => {
  const { t } = useTranslation("manualRun");
  const formatMegabytes = useFormatMegabytes();

  return useMemo((): ApiErrorMessages => {
    return {
      OPEN_GAPS_BLOCK_RUN: t("errors.openGaps"),
      NO_READY_CASES: t("errors.noReadyCases"),
      RUN_ALREADY_RUNNING: t("errors.alreadyRunning"),
      CASE_NOT_READY: t("errors.caseNotReady"),
      CASE_RESULT_EXISTS: t("errors.resultExists"),
      RUN_NOT_RUNNING: t("errors.notRunning"),
      RUN_NOT_OWNED: t("errors.notOwned"),
      RUN_NOT_MANUAL: t("errors.notManual"),
      RUN_NOT_FINISHED: t("errors.notFinished"),
      NO_FAILED_CASES_TO_RERUN: t("errors.noFailedCases"),
      UPLOAD_NOT_COMPLETED: t("errors.uploadNotCompleted"),
      FILE_TYPE_NOT_ALLOWED: t("errors.fileTypeNotAllowed"),
      FILE_TOO_LARGE: t("errors.fileTooLarge", { size: formatMegabytes(MAX_FILE_SIZE_IN_BYTES) }),
    };
  }, [formatMegabytes, t]);
};
