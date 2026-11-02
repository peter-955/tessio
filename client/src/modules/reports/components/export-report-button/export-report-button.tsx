"use client";

import { DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import type { ReportExportTarget } from "../../typing/types/report-export-target.type";
import type { ReportExport } from "../../typing/types/report.type";
import { checkCanExportReport } from "../../utils/report-permission.util";
import { ExportReportModal } from "../export-report-modal/export-report-modal";

interface Props {
  target: ReportExportTarget;
}

export const ExportReportButton: FC<Props> = ({ target }) => {
  const { t } = useTranslation("reports");
  const project = useCurrentProject();
  const [isOpened, setIsOpened] = useState(false);
  const [lastExport, setLastExport] = useState<ReportExport | null>(null);

  if (!checkCanExportReport(project)) {
    return null;
  }

  return (
    <>
      <DSButton
        type="default"
        icon="download"
        ariaHasPopup="dialog"
        onClick={() => {
          setIsOpened(true);
        }}
      >
        {t("button")}
      </DSButton>
      {isOpened && (
        <ExportReportModal
          projectKey={project.key}
          target={target}
          lastExport={lastExport}
          onExported={setLastExport}
          onClose={() => {
            setIsOpened(false);
          }}
        />
      )}
    </>
  );
};
