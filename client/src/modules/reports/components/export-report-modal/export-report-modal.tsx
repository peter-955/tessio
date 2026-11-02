"use client";

import { DSModal, DSSegmentedControl, DSStack, DSText } from "@/components/design-system";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostReportExport } from "../../hooks/mutations/use-post-report-export";
import { DEFAULT_REPORT_FORMAT, REPORT_FORMATS } from "../../typing/constants/report.constant";
import type { ReportExportTarget } from "../../typing/types/report-export-target.type";
import type { ReportExport, ReportFormat } from "../../typing/types/report.type";
import { ReportExportStatus } from "../report-export-status/report-export-status";
import styles from "./export-report-modal.module.scss";

interface Props {
  projectKey: string;
  target: ReportExportTarget;
  lastExport: ReportExport | null;
  onExported: (reportExport: ReportExport) => void;
  onClose: () => void;
}

export const ExportReportModal: FC<Props> = ({
  projectKey,
  target,
  lastExport,
  onExported,
  onClose,
}) => {
  const { t } = useTranslation("reports");
  const [format, setFormat] = useState<ReportFormat>(DEFAULT_REPORT_FORMAT);
  const exportReport = usePostReportExport(projectKey, target, { onSuccess: onExported });

  return (
    <DSModal
      isOpened
      onClose={onClose}
      title={t(`modal.title.${target.source}`)}
      cancelLabel={t("modal.close")}
      action={{
        label: t("modal.export"),
        icon: "download",
        isLoading: exportReport.isPending,
        onClick: () => {
          exportReport.mutate(format);
        },
      }}
    >
      <DSStack gap={4}>
        <DSText size="sm">{t("modal.description")}</DSText>
        <div className={styles.format}>
          <DSText size="sm" weight="medium" component="span">
            {t("modal.formatLabel")}
          </DSText>
          <DSSegmentedControl
            value={format}
            options={REPORT_FORMATS.map((value) => {
              return { value, label: t(`format.${value}`) };
            })}
            onChange={setFormat}
            ariaLabel={t("modal.formatLabel")}
          />
        </div>
        {lastExport !== null && (
          <ReportExportStatus
            key={lastExport.fileId}
            projectKey={projectKey}
            reportExport={lastExport}
          />
        )}
      </DSStack>
    </DSModal>
  );
};
