"use client";

import { DSBadge, DSStack, DSTitle } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { TEST_STATUS_COLORS } from "../../typing/constants/dashboard.constant";
import type { TestStatusRow } from "../../typing/types/dashboard.type";
import styles from "./test-status-breakdown.module.scss";

interface Props {
  rows: TestStatusRow[];
}

export const TestStatusBreakdown: FC<Props> = ({ rows }) => {
  const { t } = useTranslation("dashboard");

  return (
    <DSStack gap={2}>
      <DSTitle order={3} type="section">
        {t("testStatus.title")}
      </DSTitle>
      <ul className={styles.list}>
        {rows.map((row) => {
          return (
            <li key={row.status}>
              <Link href={row.href} className={styles.row}>
                <DSBadge color={TEST_STATUS_COLORS[row.status]} hasDot>
                  {t(`testStatus.${row.status}`)}
                </DSBadge>
                <span className={styles.count}>{row.count}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </DSStack>
  );
};
