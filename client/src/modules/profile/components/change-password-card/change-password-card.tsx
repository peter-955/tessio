"use client";

import {
  DSAlert,
  DSButton,
  DSCard,
  DSPasswordInput,
  DSStack,
  hasLength,
  isNotEmpty,
  matchesField,
  useDSForm,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { MINIMUM_PASSWORD_LENGTH } from "@/modules/auth/typing/constants/auth-form.constant";
import { useShowToast } from "@/shared/hooks/use-show-toast";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { usePutMePassword } from "../../hooks/mutations/use-put-me-password";
import type { ChangePasswordValues } from "../../typing/types/change-password-values.type";
import styles from "./change-password-card.module.scss";

export const ChangePasswordCard: FC = () => {
  const { t } = useTranslation("profile");
  const resolveMessage = useResolveApiErrorMessage();
  const { showSuccessToast } = useShowToast();
  const [serverError, setServerError] = useState<string | null>(null);
  const form = useDSForm<ChangePasswordValues>({
    mode: "controlled",
    initialValues: { currentPassword: "", newPassword: "", confirmation: "" },
    validate: {
      currentPassword: isNotEmpty(t("password.currentRequired")),
      newPassword: hasLength({ min: MINIMUM_PASSWORD_LENGTH }, t("password.tooShort")),
      confirmation: matchesField("newPassword", t("password.mismatch")),
    },
  });

  const handleError = (error: ApiError): void => {
    const message = resolveMessage(error);
    if (error.code === "INVALID_CURRENT_PASSWORD") {
      form.setFieldError("currentPassword", message);
      return;
    }
    if (error.code === "WEAK_PASSWORD" || error.code === "PASSWORD_BREACHED") {
      form.setFieldError("newPassword", message);
      return;
    }
    setServerError(message);
  };

  const changePassword = usePutMePassword({
    onSuccess: () => {
      form.reset();
      showSuccessToast(t("password.changed"), t("password.otherDevicesSignedOut"));
    },
    onError: handleError,
  });

  const handleValidSubmit = (values: ChangePasswordValues): void => {
    setServerError(null);
    changePassword.mutate({
      currentPassword: values.currentPassword,
      newPassword: values.newPassword,
    });
  };

  const handleCurrentPasswordChange = (value: string): void => {
    form.setFieldValue("currentPassword", value);
  };

  const handleNewPasswordChange = (value: string): void => {
    form.setFieldValue("newPassword", value);
  };

  const handleConfirmationChange = (value: string): void => {
    form.setFieldValue("confirmation", value);
  };

  return (
    <DSCard title={t("password.title")}>
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate className={styles.form}>
        <DSStack gap={4}>
          {serverError !== null && <DSAlert color="danger">{serverError}</DSAlert>}
          <DSPasswordInput
            label={t("password.current")}
            value={form.values.currentPassword}
            onChange={handleCurrentPasswordChange}
            error={form.errors.currentPassword}
            autoComplete="current-password"
            isRequired
          />
          <DSPasswordInput
            label={t("password.new")}
            description={t("password.rule")}
            value={form.values.newPassword}
            onChange={handleNewPasswordChange}
            error={form.errors.newPassword}
            autoComplete="new-password"
            isRequired
          />
          <DSPasswordInput
            label={t("password.confirm")}
            value={form.values.confirmation}
            onChange={handleConfirmationChange}
            error={form.errors.confirmation}
            autoComplete="new-password"
            isRequired
          />
          <div>
            <DSButton type="primary" nativeType="submit" isLoading={changePassword.isPending}>
              {t("password.submit")}
            </DSButton>
          </div>
        </DSStack>
      </form>
    </DSCard>
  );
};
