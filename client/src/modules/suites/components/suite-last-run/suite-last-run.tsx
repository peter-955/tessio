"use client";

import { DSText } from "@/components/design-system";
import { StatusBadge } from "@/components/status-badge/status-badge";
import { buildRunPath } from "@/modules/runs/utils/run-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { SuiteRunReference } from "../../typing/types/suite.type";
import styles from "./suite-last-run.module.scss";

interface Props {
  projectKey: string;
  run: SuiteRunReference | null;
}

export const SuiteLastRun: FC<Props> = ({ projectKey, run }) => {
  const { t } = useTranslation("suites");
  const formatDate = useFormatDate();

  if (run === null) {
    return (
      <DSText size="sm" color="muted" component="span">
        {t("list.neverRun")}
      </DSText>
    );
  }

  return (
    <span className={styles.run}>
      <StatusBadge status={run.status} />
      <Link href={buildRunPath(projectKey, run.id)} className={styles.link}>
        {formatDate(run.startedAt)}
      </Link>
    </span>
  );
};
