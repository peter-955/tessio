"use client";

import { DSBadge, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { Failure } from "../../typing/types/failure.type";
import styles from "./failure-assignee.module.scss";

interface Props {
  failure: Pick<Failure, "assigneeName" | "assigneeStatus">;
}

export const FailureAssignee: FC<Props> = ({ failure }) => {
  const { t } = useTranslation("failures");

  if (failure.assigneeName === null) {
    return (
      <DSText size="sm" color="muted" component="span">
        {t("assignee.unassigned")}
      </DSText>
    );
  }

  return (
    <span className={styles.assignee}>
      <span>{failure.assigneeName}</span>
      {failure.assigneeStatus === "deactivated" && (
        <DSBadge color="gray">{t("assignee.deactivated")}</DSBadge>
      )}
    </span>
  );
};
