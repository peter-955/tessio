"use client";

import { DSCard, DSSkeleton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { GAP_SKELETON_INDEXES } from "../../typing/constants/gap.constant";
import styles from "./gap-list-skeleton.module.scss";

export const GapListSkeleton: FC = () => {
  const { t } = useTranslation("gaps");

  return (
    <div role="status" aria-busy="true" aria-label={t("loading")} className={styles.list}>
      {GAP_SKELETON_INDEXES.map((index) => {
        return (
          <DSCard key={index}>
            <DSSkeleton lineCount={3} />
          </DSCard>
        );
      })}
    </div>
  );
};
