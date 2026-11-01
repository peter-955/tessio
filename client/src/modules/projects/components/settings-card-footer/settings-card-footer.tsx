"use client";

import { DSButton, DSGroup } from "@/components/design-system";
import type { FC, ReactNode } from "react";
import { useTranslation } from "react-i18next";

interface Props {
  isDirty: boolean;
  isSaving: boolean;
  children?: ReactNode;
}

export const SettingsCardFooter: FC<Props> = ({ isDirty, isSaving, children }) => {
  const { t } = useTranslation("projects");

  return (
    <DSGroup justify="end" gap={2} isWrapping>
      {children}
      <DSButton
        type="primary"
        nativeType="submit"
        icon="check"
        isDisabled={!isDirty}
        isLoading={isSaving}
      >
        {t("settings.save")}
      </DSButton>
    </DSGroup>
  );
};
