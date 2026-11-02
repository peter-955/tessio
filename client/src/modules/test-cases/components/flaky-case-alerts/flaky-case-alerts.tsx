"use client";

import { DSAlert, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetProjectMembers } from "@/shared/hooks/queries/use-get-project-members";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { TestCaseDetail } from "../../typing/types/test-case.type";
import styles from "./flaky-case-alerts.module.scss";

interface Props {
  detail: TestCaseDetail;
}

export const FlakyCaseAlerts: FC<Props> = ({ detail }) => {
  const { t } = useTranslation("flakyCases");
  const project = useCurrentProject();
  const formatDate = useFormatDate();
  const { data: members = [] } = useGetProjectMembers(project.key);
  const quarantinedByName =
    members.find((member) => member.userId === detail.quarantinedBy)?.name ??
    t("alerts.formerMember");

  if (!detail.isFlaky && !detail.isDisagreeing && !detail.isQuarantined) {
    return null;
  }

  return (
    <div className={styles.alerts}>
      {detail.isQuarantined && detail.quarantinedAt !== null && (
        <DSAlert color="info" title={t("alerts.quarantinedTitle")}>
          <span className={styles.lines}>
            <DSText component="span">
              {t("alerts.quarantined", {
                date: formatDate(detail.quarantinedAt),
                name: quarantinedByName,
              })}
            </DSText>
            {detail.quarantineReason !== null && (
              <DSText component="span">
                {t("alerts.quarantinedReason", { reason: detail.quarantineReason })}
              </DSText>
            )}
            <DSText component="span" size="sm">
              {t("alerts.quarantineNote")}
            </DSText>
          </span>
        </DSAlert>
      )}
      {detail.isFlaky && detail.flakySince !== null && (
        <DSAlert color="warning" title={t("alerts.flakyTitle")}>
          {t("alerts.flaky", { count: detail.flakyScore, date: formatDate(detail.flakySince) })}
        </DSAlert>
      )}
      {detail.isDisagreeing && detail.disagreedAt !== null && (
        <DSAlert color="warning" title={t("alerts.disagreeingTitle")}>
          {t("alerts.disagreeing", { date: formatDate(detail.disagreedAt) })}
        </DSAlert>
      )}
    </div>
  );
};
