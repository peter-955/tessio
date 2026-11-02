"use client";

import { DSBadge } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildSuitePath } from "../../utils/suite-path.util";
import styles from "./suite-run-target.module.scss";

interface Props {
  projectKey: string;
  suiteId: string;
  suiteName: string;
}

export const SuiteRunTarget: FC<Props> = ({ projectKey, suiteId, suiteName }) => {
  const { t } = useTranslation("suites");

  return (
    <span className={styles.target}>
      <DSBadge color="violet">{t("runs.suiteBadge")}</DSBadge>
      <Link href={buildSuitePath(projectKey, suiteId)} className={styles.name} title={suiteName}>
        {suiteName}
      </Link>
    </span>
  );
};
