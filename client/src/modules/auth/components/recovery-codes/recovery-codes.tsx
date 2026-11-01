"use client";

import {
  DSButton,
  DSCheckbox,
  DSCopyButton,
  DSGroup,
  DSStack,
  DSText,
  DSTitle,
} from "@/components/design-system";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { RECOVERY_CODES_FILE_NAME } from "../../typing/constants/auth-form.constant";
import { downloadTextFile } from "../../utils/download-text-file.util";
import styles from "./recovery-codes.module.scss";

interface Props {
  codes: readonly string[];
  onContinue: () => void;
}

export const RecoveryCodes: FC<Props> = ({ codes, onContinue }) => {
  const { t } = useTranslation("auth");
  const [isSaved, setIsSaved] = useState(false);
  const codesText = codes.join("\n");

  const handleDownload = (): void => {
    downloadTextFile(RECOVERY_CODES_FILE_NAME, `${codesText}\n`);
  };

  return (
    <DSStack gap={4}>
      <DSStack gap={2}>
        <DSTitle order={2} type="section">
          {t("recoveryCodes.title")}
        </DSTitle>
        <DSText size="sm" color="muted">
          {t("recoveryCodes.description")}
        </DSText>
      </DSStack>
      <ul className={styles.list} aria-label={t("recoveryCodes.listLabel")}>
        {codes.map((code) => {
          return (
            <li key={code} className={styles.code}>
              {code}
            </li>
          );
        })}
      </ul>
      <DSGroup gap={2} isWrapping>
        <DSCopyButton value={codesText} label={t("recoveryCodes.copy")} />
        <DSButton type="default" onClick={handleDownload}>
          {t("recoveryCodes.download")}
        </DSButton>
      </DSGroup>
      <DSCheckbox label={t("recoveryCodes.saved")} isChecked={isSaved} onChange={setIsSaved} />
      <DSButton type="primary" isDisabled={!isSaved} isFullWidth onClick={onContinue}>
        {t("recoveryCodes.continue")}
      </DSButton>
    </DSStack>
  );
};
