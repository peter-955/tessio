"use client";

import { DSButton, DSCard, DSStack, DSText } from "@/components/design-system";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { SignOutAllConfirm } from "../sign-out-all-confirm/sign-out-all-confirm";

export const SessionsCard: FC = () => {
  const { t } = useTranslation("profile");
  const [isConfirmOpened, setIsConfirmOpened] = useState(false);

  const handleOpen = (): void => {
    setIsConfirmOpened(true);
  };

  const handleClose = (): void => {
    setIsConfirmOpened(false);
  };

  return (
    <DSCard title={t("sessions.title")}>
      <DSStack gap={3} align="start">
        <DSText size="sm" color="muted">
          {t("sessions.description")}
        </DSText>
        <DSButton type="danger" icon="logout" onClick={handleOpen}>
          {t("sessions.action")}
        </DSButton>
      </DSStack>
      <SignOutAllConfirm isOpened={isConfirmOpened} onClose={handleClose} />
    </DSCard>
  );
};
