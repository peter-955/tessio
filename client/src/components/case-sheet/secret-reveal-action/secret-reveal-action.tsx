"use client";

import { DSActionIcon, DSTooltip } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { CaseSecretReveal } from "../typing/types/case-sheet.type";
import styles from "./secret-reveal-action.module.scss";

interface Props {
  dataKey: string;
  isRevealed: boolean;
  secretReveal: CaseSecretReveal;
}

export const SecretRevealAction: FC<Props> = ({ dataKey, isRevealed, secretReveal }) => {
  const { t } = useTranslation("caseSheet");

  if (!secretReveal.canReveal) {
    return (
      <DSTooltip label={t("revealOnlyRoles")}>
        <span className={styles.hint} tabIndex={0}>
          {t("revealOnlyRolesShort")}
        </span>
      </DSTooltip>
    );
  }

  if (isRevealed) {
    return (
      <DSActionIcon
        icon="eyeOff"
        ariaLabel={t("hideLabel", { key: dataKey })}
        tooltip={t("hide")}
        onClick={() => {
          secretReveal.onHide(dataKey);
        }}
      />
    );
  }

  return (
    <DSActionIcon
      icon="eye"
      ariaLabel={t("revealLabel", { key: dataKey })}
      tooltip={t("reveal")}
      isLoading={secretReveal.isRevealing(dataKey)}
      onClick={() => {
        secretReveal.onReveal(dataKey);
      }}
    />
  );
};
