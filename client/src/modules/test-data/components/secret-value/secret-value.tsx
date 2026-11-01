"use client";

import { DSActionIcon, DSCopyButton, DSText, DSTooltip } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { SECRET_MASK } from "../../typing/constants/test-data.constant";
import styles from "./secret-value.module.scss";

interface Props {
  dataKey: string;
  hasValue: boolean;
  revealedValue: string | undefined;
  canReveal: boolean;
  isRevealing: boolean;
  onReveal: () => void;
  onHide: () => void;
}

export const SecretValue: FC<Props> = ({
  dataKey,
  hasValue,
  revealedValue,
  canReveal,
  isRevealing,
  onReveal,
  onHide,
}) => {
  const { t } = useTranslation("testData");

  if (!hasValue) {
    return (
      <DSText component="span" size="sm" color="muted">
        {t("secret.noValue")}
      </DSText>
    );
  }

  if (revealedValue !== undefined) {
    return (
      <span className={styles.secret}>
        <DSTooltip label={t("secret.autoHide")}>
          <span className={styles.value}>{revealedValue}</span>
        </DSTooltip>
        <DSCopyButton value={revealedValue} />
        <DSActionIcon
          icon="eyeOff"
          ariaLabel={t("secret.hideLabel", { key: dataKey })}
          tooltip={t("actions.hide")}
          onClick={onHide}
        />
      </span>
    );
  }

  const mask = (
    <span className={styles.mask}>
      <span aria-hidden>{SECRET_MASK}</span>
      <span className={styles.visuallyHidden}>{t("secret.mask")}</span>
    </span>
  );

  if (!canReveal) {
    return (
      <span className={styles.secret}>
        <DSTooltip label={t("secret.revealOnlyRoles")}>{mask}</DSTooltip>
        <span className={styles.visuallyHidden}>{t("secret.revealOnlyRoles")}</span>
      </span>
    );
  }

  return (
    <span className={styles.secret}>
      {mask}
      <DSActionIcon
        icon="eye"
        ariaLabel={t("secret.revealLabel", { key: dataKey })}
        tooltip={t("actions.reveal")}
        isLoading={isRevealing}
        onClick={onReveal}
      />
    </span>
  );
};
