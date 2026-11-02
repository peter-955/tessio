import type { DSIconName, DSTimelineColor, DSTimelineItem } from "@/components/design-system";
import type { FailureTimelineLabels } from "../typing/types/failure-timeline-labels.type";
import type { FailureEvent } from "../typing/types/failure.type";

interface EventAppearance {
  icon: DSIconName;
  color: DSTimelineColor;
}

const FAILED_APPEARANCE: EventAppearance = { icon: "failures", color: "red" };

const resolveEventAppearance = (event: FailureEvent): EventAppearance => {
  switch (event.kind) {
    case "opened":
    case "failed_again":
      return FAILED_APPEARANCE;
    case "assigned":
      return { icon: "user", color: "tessio" };
    case "unassigned":
      return { icon: "user", color: "gray" };
    case "cause_changed":
      return { icon: "infoCircle", color: "tessio" };
    case "status_changed":
      if (event.toStatus === "verified") {
        return { icon: "circleCheck", color: "green" };
      }

      if (event.toStatus === "fixed") {
        return { icon: "check", color: "yellow" };
      }

      if (event.toStatus === "reopened") {
        return { icon: "refresh", color: "red" };
      }

      return FAILED_APPEARANCE;
  }
};

const resolveEventTitle = (event: FailureEvent, labels: FailureTimelineLabels): string => {
  switch (event.kind) {
    case "opened":
      return labels.opened;
    case "failed_again":
      return labels.failedAgain;
    case "status_changed":
      return labels.formatStatusChange(event.fromStatus, event.toStatus);
    case "assigned":
      return event.assigneeName === null
        ? labels.unassigned
        : labels.formatAssigned(event.assigneeName);
    case "unassigned":
      return labels.unassigned;
    case "cause_changed":
      return labels.formatCauseChange(event.fromCause, event.toCause);
  }
};

const resolveEventDescription = (event: FailureEvent, labels: FailureTimelineLabels): string => {
  if (event.actorId === null || event.actorName === null) {
    return labels.automatic;
  }

  return labels.formatActor(event.actorName);
};

export const buildFailureTimelineItems = (
  events: FailureEvent[],
  labels: FailureTimelineLabels,
): DSTimelineItem[] => {
  return events.map((event): DSTimelineItem => {
    return {
      key: event.id,
      title: resolveEventTitle(event, labels),
      description: resolveEventDescription(event, labels),
      time: labels.formatTime(event.createdAt),
      ...resolveEventAppearance(event),
    };
  });
};
