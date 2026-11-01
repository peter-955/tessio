"use client";

import { DSCode } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { MyWork } from "../../typing/types/my-work.type";
import { buildNewCaseHref, buildStoryHref } from "../../utils/dashboard-path.util";
import { WorkList } from "../work-list/work-list";
import styles from "./uncovered-criteria-list.module.scss";

interface Props {
  projectKey: string;
  list: MyWork["uncoveredCriteria"];
}

export const UncoveredCriteriaList: FC<Props> = ({ projectKey, list }) => {
  const { t } = useTranslation("dashboard");

  return (
    <WorkList
      title={t("myWork.uncovered.title")}
      totalCount={list.totalCount}
      itemCount={list.items.length}
      emptyLabel={t("myWork.uncovered.empty")}
    >
      {list.items.map((criterion) => {
        return (
          <li key={criterion.criterionId} className={styles.item}>
            <div className={styles.primary}>
              <DSCode>{criterion.code}</DSCode>
              <span>{criterion.text}</span>
            </div>
            <div className={styles.meta}>
              <Link
                href={buildStoryHref(projectKey, criterion.storyJiraKey)}
                className={styles.storyLink}
              >
                {criterion.storyJiraKey}
              </Link>
              <Link
                href={buildNewCaseHref(projectKey, criterion.storyJiraKey)}
                className={styles.action}
              >
                {t("myWork.uncovered.write")}
              </Link>
            </div>
          </li>
        );
      })}
    </WorkList>
  );
};
