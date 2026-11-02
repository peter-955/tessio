"use client";

import { DSButton } from "@/components/design-system";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { checkCanImportJunit } from "../../utils/junit-import-permission.util";
import { ImportJunitModal } from "../import-junit-modal/import-junit-modal";

export const ImportJunitButton: FC = () => {
  const { t } = useTranslation("junitImport");
  const project = useCurrentProject();
  const [isOpened, setIsOpened] = useState(false);

  if (!checkCanImportJunit(project)) {
    return null;
  }

  return (
    <>
      <DSButton
        type="default"
        icon="import"
        ariaHasPopup="dialog"
        onClick={() => {
          setIsOpened(true);
        }}
      >
        {t("actions.openImport")}
      </DSButton>
      {isOpened && (
        <ImportJunitModal
          onClose={() => {
            setIsOpened(false);
          }}
        />
      )}
    </>
  );
};
