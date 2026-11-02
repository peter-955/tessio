"use client";

import { DSTooltip } from "@/components/design-system";
import classNames from "classnames";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { SECRET_CHIP_MASK } from "../../typing/constants/case-sheet.constant";
import type { CaseReferences, ReferenceKind } from "../../typing/types/case-sheet.type";
import styles from "./reference-chip.module.scss";

interface Props {
  kind: ReferenceKind;
  referenceKey: string;
  references: CaseReferences;
}

export const ReferenceChip: FC<Props> = ({ kind, referenceKey, references }) => {
  const { t } = useTranslation("caseSheet");

  if (kind === "file") {
    const file = references.filesByKey.get(referenceKey);
    if (file === undefined) {
      return (
        <span className={classNames(styles.chip, styles.missing)}>
          {t("missingFile", { key: referenceKey })}
        </span>
      );
    }

    return (
      <DSTooltip label={t("fileTooltip", { key: referenceKey })}>
        <span className={styles.chip}>{file.fileName}</span>
      </DSTooltip>
    );
  }

  const dataValue = references.dataByKey.get(referenceKey);
  if (dataValue === undefined) {
    return (
      <span className={classNames(styles.chip, styles.missing)}>
        {references.environmentName === null
          ? t("missingValue", { key: referenceKey })
          : t("missingValueOn", { key: referenceKey, environment: references.environmentName })}
      </span>
    );
  }

  if (dataValue.kind === "secret") {
    const revealedValue = references.revealedValues[referenceKey];

    return (
      <DSTooltip label={t("secretTooltip", { key: referenceKey })}>
        <span className={styles.chip}>
          {revealedValue ?? (
            <>
              <span aria-hidden>{SECRET_CHIP_MASK}</span>
              <span className={styles.visuallyHidden}>
                {t("secretHidden", { key: referenceKey })}
              </span>
            </>
          )}
        </span>
      </DSTooltip>
    );
  }

  return (
    <DSTooltip label={t("valueTooltip", { key: referenceKey })}>
      <span className={styles.chip}>{dataValue.value}</span>
    </DSTooltip>
  );
};
