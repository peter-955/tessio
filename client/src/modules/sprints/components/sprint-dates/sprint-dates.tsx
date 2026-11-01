"use client";

import { useFormatDay } from "@/modules/stories/hooks/use-format-day";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MISSING_SPRINT_DATE } from "../../typing/constants/sprint.constant";
import type { Sprint } from "../../typing/types/sprint.type";
import styles from "./sprint-dates.module.scss";

interface Props {
  sprint: Pick<Sprint, "state" | "startAt" | "endAt" | "completeAt">;
}

export const SprintDates: FC<Props> = ({ sprint }) => {
  const { t } = useTranslation("sprints");
  const formatDay = useFormatDay();
  const isNotSet = sprint.startAt === null && sprint.endAt === null;

  const formatOptionalDay = (isoDate: string | null): string => {
    return isoDate === null ? MISSING_SPRINT_DATE : formatDay(isoDate);
  };

  return (
    <span className={styles.dates}>
      {isNotSet ? (
        <span className={styles.muted}>{t("dates.notSet")}</span>
      ) : (
        <span>
          {t("dates.range", {
            start: formatOptionalDay(sprint.startAt),
            end: formatOptionalDay(sprint.endAt),
          })}
        </span>
      )}
      {sprint.state === "closed" && sprint.completeAt !== null && (
        <span className={styles.muted}>
          {t("dates.completed", { date: formatDay(sprint.completeAt) })}
        </span>
      )}
    </span>
  );
};
