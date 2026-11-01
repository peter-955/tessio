"use client";

import { DSBadge, DSCard, DSGroup, DSStack, DSText } from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { JiraConnection } from "../../typing/types/jira-connection.type";
import { JiraConnectionForm } from "../jira-connection-form/jira-connection-form";
import styles from "./jira-connection-card.module.scss";

interface Props {
  connection: JiraConnection;
}

export const JiraConnectionCard: FC<Props> = ({ connection }) => {
  const { t } = useTranslation("settings");
  const formatDate = useFormatDate();

  return (
    <DSCard title={t("jira.title")} className={styles.card}>
      <DSStack gap={5}>
        <DSGroup gap={2} isWrapping>
          {connection.isConfigured ? (
            <>
              <DSBadge color="green" hasDot>
                {t("jira.connected")}
              </DSBadge>
              <DSText size="sm" color="muted" component="span" className={styles.details}>
                {t("jira.connectedAs", {
                  name: connection.accountDisplayName ?? connection.accountEmail ?? "",
                  email: connection.accountEmail ?? "",
                  siteUrl: connection.siteUrl ?? "",
                  date: connection.configuredAt ? formatDate(connection.configuredAt) : "",
                })}
              </DSText>
            </>
          ) : (
            <DSBadge hasDot>{t("jira.notConnected")}</DSBadge>
          )}
        </DSGroup>
        <JiraConnectionForm connection={connection} />
      </DSStack>
    </DSCard>
  );
};
