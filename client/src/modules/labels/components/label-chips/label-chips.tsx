"use client";

import classNames from "classnames";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseLabel } from "../../typing/types/label.type";
import { LabelChip } from "../label-chip/label-chip";
import styles from "./label-chips.module.scss";

interface Props {
  labels: readonly CaseLabel[];
  className?: string;
}

export const LabelChips: FC<Props> = ({ labels, className }) => {
  const { t } = useTranslation("labels");

  if (labels.length === 0) {
    return null;
  }

  return (
    <ul className={classNames(styles.chips, className)} aria-label={t("chips.ariaLabel")}>
      {labels.map((label) => {
        return (
          <li key={label.id}>
            <LabelChip name={label.name} color={label.color} />
          </li>
        );
      })}
    </ul>
  );
};
