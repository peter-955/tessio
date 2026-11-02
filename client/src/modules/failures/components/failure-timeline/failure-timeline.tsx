"use client";

import { DSCard, DSTimeline } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import { useMemo, type FC } from "react";
import { useTranslation } from "react-i18next";
import { EMPTY_VALUE } from "../../typing/constants/failure.constant";
import type { FailureEvent, FailureStatus } from "../../typing/types/failure.type";
import { buildFailureTimelineItems } from "../../utils/failure-event.util";

interface Props {
  events: FailureEvent[];
}

export const FailureTimeline: FC<Props> = ({ events }) => {
  const { t } = useTranslation("failures");
  const { t: translateDiagnosis } = useTranslation("diagnosis");
  const formatDate = useFormatDate();
  const items = useMemo(() => {
    const formatStatus = (status: FailureStatus | null): string => {
      return status === null ? EMPTY_VALUE : t(`status.${status}`);
    };

    return buildFailureTimelineItems(events, {
      opened: t("timeline.opened"),
      failedAgain: t("timeline.failedAgain"),
      unassigned: t("timeline.unassigned"),
      automatic: t("timeline.automatic"),
      formatStatusChange: (fromStatus, toStatus) => {
        return t("timeline.statusChanged", {
          from: formatStatus(fromStatus),
          to: formatStatus(toStatus),
        });
      },
      formatAssigned: (name) => {
        return t("timeline.assigned", { name });
      },
      formatCauseChange: (fromCause, toCause) => {
        return t("timeline.causeChanged", {
          from: fromCause === null ? EMPTY_VALUE : translateDiagnosis(`cause.${fromCause}`),
          to: toCause === null ? EMPTY_VALUE : translateDiagnosis(`cause.${toCause}`),
        });
      },
      formatActor: (name) => {
        return t("timeline.by", { name });
      },
      formatTime: formatDate,
    });
  }, [events, formatDate, t, translateDiagnosis]);

  return (
    <DSCard title={t("timeline.title")}>
      <DSTimeline items={items} activeIndex={items.length - 1} />
    </DSCard>
  );
};
