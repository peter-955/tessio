"use client";

import {
  DSErrorState,
  DSSkeleton,
  DSTimeline,
  type DSTimelineItem,
} from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useId, type FC } from "react";
import { useTranslation } from "react-i18next";
import { useGetQuarantineEvents } from "../../hooks/queries/use-get-quarantine-events";
import type { QuarantineEvent } from "../../typing/types/quarantine.type";
import styles from "./quarantine-history.module.scss";

interface Props {
  caseCode: string;
}

export const QuarantineHistory: FC<Props> = ({ caseCode }) => {
  const { t } = useTranslation("flakyCases");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const titleId = useId();
  const { data, isPending, isError, isFetching, refetch } = useGetQuarantineEvents(
    project.key,
    caseCode,
  );

  if (isPending) {
    return (
      <div aria-busy="true">
        <DSSkeleton lineCount={2} />
      </div>
    );
  }

  if (isError || data === undefined) {
    return (
      <DSErrorState
        title={t("history.loadError")}
        retryLabel={t("history.retry")}
        isRetrying={isFetching}
        onRetry={() => {
          void refetch();
        }}
      />
    );
  }

  if (data.length === 0) {
    return null;
  }

  const buildTitle = (event: QuarantineEvent): string => {
    const name = event.actorName ?? t("history.formerMember");

    switch (event.kind) {
      case "quarantined":
        return t("history.quarantined", { name });
      case "released":
        return t("history.released", { name });
      case "auto_released":
        return t("history.autoReleased");
    }
  };

  const items = data.map((event): DSTimelineItem => {
    return {
      key: event.id,
      title: buildTitle(event),
      description:
        event.reason === null ? undefined : t("history.reason", { reason: event.reason }),
      time: formatDate(event.createdAt),
      icon: "quarantine",
      color: event.kind === "quarantined" ? "yellow" : "green",
    };
  });

  return (
    <section aria-labelledby={titleId} className={styles.history}>
      <h2 id={titleId} className={styles.heading}>
        {t("history.title")}
      </h2>
      <DSTimeline items={items} />
    </section>
  );
};
