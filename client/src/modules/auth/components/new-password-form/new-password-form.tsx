"use client";

import {
  DSAlert,
  DSButton,
  DSPasswordInput,
  DSStack,
  hasLength,
  matchesField,
  useDSForm,
} from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { MINIMUM_PASSWORD_LENGTH } from "../../typing/constants/auth-form.constant";
import type { NewPasswordValues } from "../../typing/types/new-password-values.type";

interface Props {
  submitLabel: string;
  isSubmitting: boolean;
  serverError: string | null;
  onSubmit: (password: string) => void;
}

export const NewPasswordForm: FC<Props> = ({
  submitLabel,
  isSubmitting,
  serverError,
  onSubmit,
}) => {
  const { t } = useTranslation("auth");
  const form = useDSForm<NewPasswordValues>({
    mode: "controlled",
    initialValues: { password: "", confirmation: "" },
    validate: {
      password: hasLength({ min: MINIMUM_PASSWORD_LENGTH }, t("errors.passwordTooShort")),
      confirmation: matchesField("password", t("errors.passwordMismatch")),
    },
  });

  const handleValidSubmit = (values: NewPasswordValues): void => {
    onSubmit(values.password);
  };

  const handlePasswordChange = (value: string): void => {
    form.setFieldValue("password", value);
  };

  const handleConfirmationChange = (value: string): void => {
    form.setFieldValue("confirmation", value);
  };

  return (
    <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
      <DSStack gap={4}>
        {serverError !== null && <DSAlert color="danger">{serverError}</DSAlert>}
        <DSPasswordInput
          label={t("newPassword.password")}
          description={t("newPassword.rule")}
          value={form.values.password}
          onChange={handlePasswordChange}
          error={form.errors.password}
          autoComplete="new-password"
          isRequired
          isAutoFocused
        />
        <DSPasswordInput
          label={t("newPassword.confirm")}
          value={form.values.confirmation}
          onChange={handleConfirmationChange}
          error={form.errors.confirmation}
          autoComplete="new-password"
          isRequired
        />
        <DSButton type="primary" nativeType="submit" isLoading={isSubmitting} isFullWidth>
          {submitLabel}
        </DSButton>
      </DSStack>
    </form>
  );
};
