"use client";

import { DSIcon, DSText } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildUnassignedFailuresHref } from "../../utils/dashboard-path.util";
import styles from "./unassigned-failures.module.scss";

interface Props {
  projectKey: string;
  count: number;
}

export const UnassignedFailures: FC<Props> = ({ projectKey, count }) => {
  const { t } = useTranslation("dashboard");

  return (
    <div className={styles.box}>
      <DSIcon name="alertCircle" size={16} />
      {count === 0 ? (
        <DSText size="sm" color="muted" component="span">
          {t("myWork.noUnassigned")}
        </DSText>
      ) : (
        <Link href={buildUnassignedFailuresHref(projectKey)} className={styles.link}>
          {t("myWork.unassigned", { count })}
        </Link>
      )}
    </div>
  );
};
