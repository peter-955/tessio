"use client";

import { DSBadge } from "@/components/design-system";
import { buildStoryGapsHref } from "@/modules/gaps/utils/gap-path.util";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { GAP_INBOX_PATH, GAP_SEVERITY_COLORS } from "../../typing/constants/dashboard.constant";
import type { MyWork } from "../../typing/types/my-work.type";
import { WorkList } from "../work-list/work-list";
import styles from "./gaps-to-answer-list.module.scss";

interface Props {
  projectKey: string;
  list: MyWork["gapsToAnswer"];
}

export const GapsToAnswerList: FC<Props> = ({ projectKey, list }) => {
  const { t } = useTranslation("dashboard");
  const formatDate = useFormatDate();

  return (
    <WorkList
      title={t("myWork.gaps.title")}
      totalCount={list.totalCount}
      itemCount={list.items.length}
      emptyLabel={t("myWork.gaps.empty")}
      viewAllHref={GAP_INBOX_PATH}
    >
      {list.items.map((gap) => {
        return (
          <li key={gap.gapId} className={styles.item}>
            <div className={styles.primary}>
              <Link href={buildStoryGapsHref(projectKey, gap.storyJiraKey)} className={styles.link}>
                {gap.question}
              </Link>
            </div>
            <div className={styles.meta}>
              <DSBadge color={GAP_SEVERITY_COLORS[gap.severity]}>
                {t(`statuses.severity.${gap.severity}`)}
              </DSBadge>
              <span>{t(`statuses.gapType.${gap.type}`)}</span>
              <span>{gap.storyJiraKey}</span>
              <span>{formatDate(gap.createdAt)}</span>
            </div>
          </li>
        );
      })}
    </WorkList>
  );
};
