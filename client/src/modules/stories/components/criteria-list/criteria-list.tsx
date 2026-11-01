"use client";

import { DSBadge, DSEmptyState } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useFormatDay } from "../../hooks/use-format-day";
import type { AcceptanceCriterion } from "../../typing/types/story.type";
import { sortCriteria } from "../../utils/criteria.util";
import styles from "./criteria-list.module.scss";

interface Props {
  criteria: AcceptanceCriterion[];
}

export const CriteriaList: FC<Props> = ({ criteria }) => {
  const { t } = useTranslation("stories");
  const formatDay = useFormatDay();

  if (criteria.length === 0) {
    return (
      <DSEmptyState
        size="sm"
        title={t("criteria.empty.title")}
        description={t("criteria.empty.description")}
        icon="file"
      />
    );
  }

  return (
    <ol className={styles.list}>
      {sortCriteria(criteria).map((criterion) => {
        return (
          <li key={criterion.id} className={styles.item}>
            <DSBadge color="tessio">{criterion.code}</DSBadge>
            {criterion.isRemoved ? (
              <span className={styles.removed}>
                <s className={styles.text}>{criterion.text}</s>
                <DSBadge>
                  {t("criteria.removed", {
                    date: criterion.removedAt === null ? "" : formatDay(criterion.removedAt),
                  })}
                </DSBadge>
              </span>
            ) : (
              <span className={styles.text}>{criterion.text}</span>
            )}
          </li>
        );
      })}
    </ol>
  );
};
