"use client";

import { DSImage, DSSkeleton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetScreenshotLink } from "../../../hooks/queries/use-get-screenshot-link";
import styles from "./linked-screenshot.module.scss";

const SKELETON_HEIGHT = 160;

interface Props {
  fileId: string;
  order: number;
}

export const LinkedScreenshot: FC<Props> = ({ fileId, order }) => {
  const { t } = useTranslation("failures");
  const project = useCurrentProject();
  const link = useGetScreenshotLink(project.key, fileId, true);

  if (link.isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton height={SKELETON_HEIGHT} />
      </div>
    );
  }

  return (
    <div className={styles.screenshot}>
      <DSImage
        src={link.data?.url ?? null}
        alt={t("screenshot.alt", { order })}
        fallbackLabel={t("screenshot.unavailable")}
        fit="contain"
        isZoomable
        closeLabel={t("screenshot.close")}
      />
    </div>
  );
};
