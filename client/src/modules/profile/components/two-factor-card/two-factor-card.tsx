"use client";

import { DSAlert, DSButton, DSCard, DSModal, DSStack, DSText } from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { RecoveryCodes } from "@/modules/auth/components/recovery-codes/recovery-codes";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePostRecoveryCodes } from "../../hooks/mutations/use-post-recovery-codes";
import { usePostTwoFactorReset } from "../../hooks/mutations/use-post-two-factor-reset";
import { PasswordConfirmDialog } from "../password-confirm-dialog/password-confirm-dialog";
import styles from "./two-factor-card.module.scss";

type TwoFactorAction = "regenerate" | "reset";

export const TwoFactorCard: FC = () => {
  const { t } = useTranslation("profile");
  const resolveMessage = useResolveApiErrorMessage();
  const [openedAction, setOpenedAction] = useState<TwoFactorAction | null>(null);
  const [dialogKey, setDialogKey] = useState(0);
  const regenerateCodes = usePostRecoveryCodes();
  const resetTwoFactor = usePostTwoFactorReset();
  const recoveryCodes = regenerateCodes.data;

  const openAction = (action: TwoFactorAction): void => {
    regenerateCodes.reset();
    resetTwoFactor.reset();
    setDialogKey((key) => {
      return key + 1;
    });
    setOpenedAction(action);
  };

  const handleOpenRegenerate = (): void => {
    openAction("regenerate");
  };

  const handleOpenReset = (): void => {
    openAction("reset");
  };

  const handleClose = (): void => {
    setOpenedAction(null);
    regenerateCodes.reset();
    resetTwoFactor.reset();
  };

  const handleRegenerate = (password: string): void => {
    regenerateCodes.mutate({ password });
  };

  const handleReset = (password: string): void => {
    resetTwoFactor.mutate({ password });
  };

  return (
    <DSCard title={t("twoFactor.title")}>
      <DSStack gap={4}>
        <div className={styles.action}>
          <DSStack gap={1}>
            <DSText weight="medium">{t("twoFactor.regenerate")}</DSText>
            <DSText size="sm" color="muted">
              {t("twoFactor.regenerateDescription")}
            </DSText>
          </DSStack>
          <DSButton type="default" icon="refresh" onClick={handleOpenRegenerate}>
            {t("twoFactor.regenerate")}
          </DSButton>
        </div>
        <div className={styles.action}>
          <DSStack gap={1}>
            <DSText weight="medium">{t("twoFactor.reset")}</DSText>
            <DSText size="sm" color="muted">
              {t("twoFactor.resetDescription")}
            </DSText>
          </DSStack>
          <DSButton type="danger" icon="lock" onClick={handleOpenReset}>
            {t("twoFactor.reset")}
          </DSButton>
        </div>
      </DSStack>
      <PasswordConfirmDialog
        key={`regenerate-${dialogKey}`}
        isOpened={openedAction === "regenerate" && recoveryCodes === undefined}
        title={t("twoFactor.regenerate")}
        description={t("twoFactor.regenerateDescription")}
        confirmLabel={t("twoFactor.confirm")}
        isPending={regenerateCodes.isPending}
        serverError={regenerateCodes.error ? resolveMessage(regenerateCodes.error) : null}
        onConfirm={handleRegenerate}
        onClose={handleClose}
      />
      <DSModal
        isOpened={openedAction === "regenerate" && recoveryCodes !== undefined}
        onClose={handleClose}
        title={t("twoFactor.regenerate")}
        hasCancelButton={false}
        isCloseDisabled
      >
        {recoveryCodes !== undefined && (
          <RecoveryCodes codes={recoveryCodes} onContinue={handleClose} />
        )}
      </DSModal>
      <PasswordConfirmDialog
        key={`reset-${dialogKey}`}
        isOpened={openedAction === "reset"}
        title={t("twoFactor.reset")}
        description={t("twoFactor.resetDescription")}
        confirmLabel={t("twoFactor.confirm")}
        isPending={resetTwoFactor.isPending || resetTwoFactor.isSuccess}
        serverError={resetTwoFactor.error ? resolveMessage(resetTwoFactor.error) : null}
        onConfirm={handleReset}
        onClose={handleClose}
      >
        <DSAlert color="warning">{t("twoFactor.resetWarning")}</DSAlert>
      </PasswordConfirmDialog>
    </DSCard>
  );
};
