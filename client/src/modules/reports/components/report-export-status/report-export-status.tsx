"use client";

import { DSAlert, DSButtonLink, DSGroup, DSLoader, DSText } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useGetReportLink } from "../../hooks/queries/use-get-report-link";
import {
  NOT_FOUND_STATUS,
  REPORT_LINK_MAX_POLL_COUNT,
} from "../../typing/constants/report.constant";
import type { ReportExport } from "../../typing/types/report.type";
import { checkCanDownloadReport } from "../../utils/report-permission.util";

interface Props {
  projectKey: string;
  reportExport: ReportExport;
}

export const ReportExportStatus: FC<Props> = ({ projectKey, reportExport }) => {
  const { t } = useTranslation("reports");
  const project = useCurrentProject();
  const canDownload = checkCanDownloadReport(project);
  const { data, error, isError, errorUpdateCount } = useGetReportLink(
    projectKey,
    reportExport.fileId,
    canDownload,
  );
  const isStillPending =
    !isError ||
    (error?.status === NOT_FOUND_STATUS && errorUpdateCount < REPORT_LINK_MAX_POLL_COUNT);

  const renderBody = (): ReactNode => {
    if (data !== undefined) {
      return (
        <DSGroup gap={3} isWrapping>
          <DSText size="sm" component="span">
            {t("status.ready", { fileName: reportExport.fileName })}
          </DSText>
          <DSButtonLink href={data.url} type="primary" icon="download" isExternal>
            {t("status.download")}
          </DSButtonLink>
        </DSGroup>
      );
    }

    if (!canDownload || !isStillPending) {
      return (
        <DSText size="sm" component="span">
          {t("status.notifyLater", { fileName: reportExport.fileName })}
        </DSText>
      );
    }

    return (
      <DSGroup gap={2}>
        <DSLoader size="sm" />
        <DSText size="sm" component="span">
          {t("status.preparing", { fileName: reportExport.fileName })}
        </DSText>
      </DSGroup>
    );
  };

  return <DSAlert color={data === undefined ? "info" : "success"}>{renderBody()}</DSAlert>;
};
