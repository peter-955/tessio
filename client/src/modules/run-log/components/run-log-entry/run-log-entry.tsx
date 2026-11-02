"use client";

import { DSBadge } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { RunLogEntry } from "../../typing/types/run-log.type";
import { buildRunLogLabel, formatElapsed } from "../../utils/run-log.util";
import styles from "./run-log-entry.module.scss";

interface Props {
  entry: RunLogEntry;
  startAt: string;
}

export const RunLogEntryRow: FC<Props> = ({ entry, startAt }) => {
  const { t } = useTranslation("runs");
  const elapsed = formatElapsed(startAt, entry.at);

  if (entry.kind === "note") {
    return (
      <li className={styles.entry}>
        <span className={styles.time}>{elapsed}</span>
        <p className={styles.note}>{entry.output}</p>
      </li>
    );
  }

  const label = buildRunLogLabel(entry);

  return (
    <li className={styles.entry}>
      <span className={styles.time}>{elapsed}</span>
      <details className={styles.action}>
        <summary className={styles.summary}>
          <span>{t(label.key, { ...label.values, defaultValue: "" })}</span>
          {entry.durationMs !== null && (
            <span className={styles.duration}>
              {t("log.duration", { seconds: (entry.durationMs / 1000).toFixed(1) })}
            </span>
          )}
          {entry.isError && <DSBadge color="red">{t("log.error")}</DSBadge>}
        </summary>
        <div className={styles.details}>
          <span className={styles.detailLabel}>{t("log.tool")}</span>
          <code className={styles.code}>{entry.tool}</code>
          <span className={styles.detailLabel}>{t("log.input")}</span>
          <pre className={styles.code}>{JSON.stringify(entry.input, null, 2)}</pre>
          {entry.output !== null && (
            <>
              <span className={styles.detailLabel}>{t("log.output")}</span>
              <pre className={styles.code}>{entry.output}</pre>
            </>
          )}
        </div>
      </details>
    </li>
  );
};
