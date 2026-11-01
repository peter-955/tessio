"use client";

import { DSImage, DSLoader, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ScreenshotState } from "../../../../typing/types/run.type";
import { ScreenshotImage } from "./screenshot-image/screenshot-image";
import styles from "./step-screenshot.module.scss";

interface Props {
  projectKey: string;
  fileId: string;
  state: ScreenshotState;
  alt: string;
}

export const StepScreenshot: FC<Props> = ({ projectKey, fileId, state, alt }) => {
  const { t } = useTranslation("runs");

  if (state === "none") {
    return null;
  }

  if (state === "uploading") {
    return (
      <div className={styles.uploading} role="status">
        <DSLoader />
        <DSText size="sm" color="muted" component="span">
          {t("screenshot.uploading")}
        </DSText>
      </div>
    );
  }

  if (state === "missing") {
    return (
      <div className={styles.frame}>
        <DSImage src={null} alt={alt} fallbackLabel={t("screenshot.missing")} height={120} />
      </div>
    );
  }

  return <ScreenshotImage projectKey={projectKey} fileId={fileId} alt={alt} />;
};
