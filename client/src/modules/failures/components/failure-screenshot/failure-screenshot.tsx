"use client";

import { DSText } from "@/components/design-system";
import type { RunStatus } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { FailedStep, RunStepResult } from "../../typing/types/failure.type";
import { LinkedScreenshot } from "./linked-screenshot/linked-screenshot";

interface Props {
  failedStep: FailedStep;
  runStep: RunStepResult | null;
  runStatus: RunStatus | null;
}

export const FailureScreenshot: FC<Props> = ({ failedStep, runStep, runStatus }) => {
  const { t } = useTranslation("failures");

  if (failedStep.screenshotFileId === null) {
    return (
      <DSText size="sm" color="muted">
        {t("screenshot.none")}
      </DSText>
    );
  }

  if (runStep?.screenshotStatus === "pending" && runStatus === "running") {
    return (
      <DSText size="sm" color="muted">
        {t("screenshot.uploading")}
      </DSText>
    );
  }

  if (runStep?.screenshotStatus === "missing" || runStep?.screenshotStatus === "pending") {
    return (
      <DSText size="sm" color="warning">
        {t("screenshot.missing")}
      </DSText>
    );
  }

  return <LinkedScreenshot fileId={failedStep.screenshotFileId} order={failedStep.stepOrder} />;
};
