"use client";

import { DSText, DSTitle } from "@/components/design-system";
import Link from "next/link";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import styles from "./work-list.module.scss";

interface Props {
  title: string;
  totalCount: number;
  itemCount: number;
  emptyLabel: string;
  viewAllHref?: string;
  children: ReactNode;
}

export const WorkList: FC<Props> = ({
  title,
  totalCount,
  itemCount,
  emptyLabel,
  viewAllHref,
  children,
}) => {
  const { t } = useTranslation("dashboard");

  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <DSTitle order={3} type="section">
          {title}
        </DSTitle>
        {viewAllHref !== undefined && itemCount > 0 && (
          <Link href={viewAllHref} className={styles.viewAll}>
            {t("myWork.viewAll")}
          </Link>
        )}
      </div>
      {itemCount === 0 ? (
        <DSText size="sm" color="muted">
          {emptyLabel}
        </DSText>
      ) : (
        <ul className={styles.list}>{children}</ul>
      )}
      {totalCount > itemCount && (
        <DSText size="sm" color="muted">
          {t("myWork.showing", { count: itemCount, total: totalCount })}
        </DSText>
      )}
    </section>
  );
};
