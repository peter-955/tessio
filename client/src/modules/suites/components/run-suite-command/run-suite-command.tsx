"use client";

import { DSCard, DSCode, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { buildRunSuiteCommand } from "../../utils/suite-command.util";

interface Props {
  suite: { id: string; name: string };
}

export const RunSuiteCommand: FC<Props> = ({ suite }) => {
  const { t } = useTranslation("suites");

  return (
    <DSCard title={t("command.title")}>
      <DSStack gap={3}>
        <DSText size="sm">{t("command.description")}</DSText>
        <DSCode isBlock isCopyable>
          {buildRunSuiteCommand(suite)}
        </DSCode>
        <DSText size="sm" color="muted">
          {t("command.note")}
        </DSText>
      </DSStack>
    </DSCard>
  );
};
