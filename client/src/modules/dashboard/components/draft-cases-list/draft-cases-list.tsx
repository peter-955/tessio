"use client";

import { DSBadge, DSCode } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { CASE_STATUS_COLORS } from "../../typing/constants/dashboard.constant";
import type { MyWork } from "../../typing/types/my-work.type";
import { buildCaseHref } from "../../utils/dashboard-path.util";
import { WorkList } from "../work-list/work-list";
import styles from "./draft-cases-list.module.scss";

interface Props {
  projectKey: string;
  list: MyWork["draftCases"];
}

export const DraftCasesList: FC<Props> = ({ projectKey, list }) => {
  const { t } = useTranslation("dashboard");

  return (
    <WorkList
      title={t("myWork.drafts.title")}
      totalCount={list.totalCount}
      itemCount={list.items.length}
      emptyLabel={t("myWork.drafts.empty")}
    >
      {list.items.map((draftCase) => {
        return (
          <li key={draftCase.caseId} className={styles.item}>
            <div className={styles.primary}>
              <DSCode>{draftCase.code}</DSCode>
              <Link href={buildCaseHref(projectKey, draftCase.code)} className={styles.link}>
                {draftCase.title}
              </Link>
            </div>
            <div className={styles.meta}>
              <DSBadge color={CASE_STATUS_COLORS[draftCase.status]}>
                {t(`statuses.case.${draftCase.status}`)}
              </DSBadge>
              <span>{draftCase.storyJiraKey}</span>
            </div>
          </li>
        );
      })}
    </WorkList>
  );
};
