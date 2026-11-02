"use client";

import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import type { Notification, NotificationDescription } from "../typing/types/notification.type";

export const useDescribeNotification = (): ((
  notification: Notification,
) => NotificationDescription) => {
  const { t } = useTranslation("notifications");

  return useCallback(
    (notification: Notification): NotificationDescription => {
      const { payload } = notification;

      switch (payload.kind) {
        case "gap_assigned":
          return {
            title: t("kind.gapAssigned.title", { storyKey: payload.storyJiraKey }),
            description: t("kind.gapAssigned.description", { question: payload.question }),
          };
        case "failure_assigned":
          return {
            title: t("kind.failureAssigned.title", { storyKey: payload.storyJiraKey }),
            description: t("kind.failureAssigned.description", {
              testCaseCode: payload.testCaseCode,
              testCaseTitle: payload.testCaseTitle,
            }),
          };
        case "run_finished":
          return {
            title: t(`kind.runFinished.title.${payload.outcome}`, {
              storyKey: payload.storyJiraKey,
            }),
            description: t("kind.runFinished.description", {
              passedCount: payload.passedCount,
              failedCount: payload.failedCount,
              blockedCount: payload.blockedCount,
            }),
          };
        case "suite_run_finished":
          return {
            title: t(`kind.suiteRunFinished.title.${payload.outcome}`, {
              suiteName: payload.testSuiteName,
            }),
            description: t("kind.suiteRunFinished.description", {
              passedCount: payload.passedCount,
              failedCount: payload.failedCount,
              blockedCount: payload.blockedCount,
            }),
          };
        case "report_ready":
          return {
            title: t(`kind.reportReady.title.${payload.source}`, {
              sourceLabel: payload.sourceLabel,
            }),
            description: t("kind.reportReady.description", { fileName: payload.fileName }),
          };
        default:
          payload satisfies never;
          return { title: notification.projectName, description: "" };
      }
    },
    [t],
  );
};
