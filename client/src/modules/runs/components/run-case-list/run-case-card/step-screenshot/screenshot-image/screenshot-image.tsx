"use client";

import { DSImage, DSSkeleton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetFileLink } from "../../../../../hooks/queries/use-get-file-link";
import styles from "./screenshot-image.module.scss";

interface Props {
  projectKey: string;
  fileId: string;
  alt: string;
}

export const ScreenshotImage: FC<Props> = ({ projectKey, fileId, alt }) => {
  const { t } = useTranslation("runs");
  const { data, isPending, isError } = useGetFileLink(projectKey, fileId);

  if (isPending) {
    return (
      <div className={styles.frame} aria-busy="true">
        <DSSkeleton height={120} radius="md" />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <div className={styles.frame}>
        <DSImage src={null} alt={alt} fallbackLabel={t("screenshot.loadFailed")} height={120} />
      </div>
    );
  }

  return (
    <div className={styles.frame}>
      <DSImage
        src={data.url}
        alt={alt}
        fallbackLabel={t("screenshot.loadFailed")}
        width="100%"
        fit="contain"
        isZoomable
        closeLabel={t("screenshot.close")}
      />
    </div>
  );
};
