"use client";

import {
  DSAlert,
  DSModal,
  DSPasswordInput,
  DSStack,
  DSText,
  isNotEmpty,
  useDSForm,
} from "@/components/design-system";
import { useId, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import type { PasswordConfirmationValues } from "../../typing/types/password-confirmation-values.type";

interface Props {
  isOpened: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  isPending: boolean;
  serverError: string | null;
  onConfirm: (password: string) => void;
  onClose: () => void;
  children?: ReactNode;
}

export const PasswordConfirmDialog: FC<Props> = ({
  isOpened,
  title,
  description,
  confirmLabel,
  isPending,
  serverError,
  onConfirm,
  onClose,
  children,
}) => {
  const { t } = useTranslation("profile");
  const formId = useId();
  const form = useDSForm<PasswordConfirmationValues>({
    mode: "controlled",
    initialValues: { password: "" },
    validate: { password: isNotEmpty(t("twoFactor.passwordRequired")) },
  });

  const handlePasswordChange = (value: string): void => {
    form.setFieldValue("password", value);
  };

  const handleValidSubmit = (values: PasswordConfirmationValues): void => {
    onConfirm(values.password);
  };

  const handleClose = (): void => {
    form.reset();
    onClose();
  };

  return (
    <DSModal
      isOpened={isOpened}
      onClose={handleClose}
      title={title}
      isCloseDisabled={isPending}
      action={{ label: confirmLabel, isLoading: isPending, formId }}
    >
      <form id={formId} onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          <DSText size="sm" color="muted">
            {description}
          </DSText>
          {children}
          {serverError !== null && <DSAlert color="danger">{serverError}</DSAlert>}
          <DSPasswordInput
            label={t("twoFactor.passwordLabel")}
            value={form.values.password}
            onChange={handlePasswordChange}
            error={form.errors.password}
            autoComplete="current-password"
            isRequired
            isAutoFocused
          />
        </DSStack>
      </form>
    </DSModal>
  );
};
