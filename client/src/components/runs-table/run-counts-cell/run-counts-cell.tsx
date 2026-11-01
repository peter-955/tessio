"use client";

import { DSText } from "@/components/design-system";
import { listCountEntries } from "@/modules/runs/utils/run-counts.util";
import type { RunCounts } from "@/shared/typing/types/test-run.type";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import styles from "./run-counts-cell.module.scss";

interface Props {
  counts: RunCounts;
}

export const RunCountsCell: FC<Props> = ({ counts }) => {
  const { t } = useTranslation("runs");
  const entries = listCountEntries(counts);
  const countText = entries
    .map((entry) => {
      return t(`counts.${entry.key}`, { count: entry.count });
    })
    .join(" · ");

  return (
    <div className={styles.cell}>
      {countText !== "" && (
        <DSText size="sm" component="span">
          {countText}
        </DSText>
      )}
      <DSText size="xs" color="muted" component="span">
        {t("counts.total", { count: counts.total })}
      </DSText>
    </div>
  );
};
