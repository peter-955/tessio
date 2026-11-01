"use client";

import { DSBadge, DSCode } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { FAILURE_STATUS_COLORS } from "../../typing/constants/dashboard.constant";
import type { MyWork } from "../../typing/types/my-work.type";
import { buildFailureHref, buildFailuresHref } from "../../utils/dashboard-path.util";
import { WorkList } from "../work-list/work-list";
import styles from "./failures-to-fix-list.module.scss";

interface Props {
  projectKey: string;
  list: MyWork["failuresToFix"];
}

export const FailuresToFixList: FC<Props> = ({ projectKey, list }) => {
  const { t } = useTranslation("dashboard");
  const formatDate = useFormatDate();

  return (
    <WorkList
      title={t("myWork.failures.title")}
      totalCount={list.totalCount}
      itemCount={list.items.length}
      emptyLabel={t("myWork.failures.empty")}
      viewAllHref={buildFailuresHref(projectKey)}
    >
      {list.items.map((failure) => {
        return (
          <li key={failure.failureId} className={styles.item}>
            <div className={styles.primary}>
              <DSCode>{failure.caseCode}</DSCode>
              <Link href={buildFailureHref(projectKey, failure.failureId)} className={styles.link}>
                {failure.caseTitle}
              </Link>
            </div>
            <div className={styles.meta}>
              <DSBadge color={FAILURE_STATUS_COLORS[failure.status]}>
                {t(`statuses.failure.${failure.status}`)}
              </DSBadge>
              <span>{failure.storyJiraKey}</span>
              <span>{t("myWork.failures.opened", { date: formatDate(failure.openedAt) })}</span>
            </div>
          </li>
        );
      })}
    </WorkList>
  );
};
