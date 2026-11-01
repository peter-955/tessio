"use client";

import { DSButton } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { useOpenEvidence } from "../../../../hooks/mutations/use-open-evidence";

interface Props {
  projectKey: string;
  fileId: string;
}

export const StepEvidence: FC<Props> = ({ projectKey, fileId }) => {
  const { t } = useTranslation("runs");
  const { mutate, isPending } = useOpenEvidence(projectKey);

  return (
    <DSButton
      type="outline"
      icon="file"
      isLoading={isPending}
      onClick={() => {
        mutate(fileId);
      }}
    >
      {t("screenshot.openEvidence")}
    </DSButton>
  );
};
