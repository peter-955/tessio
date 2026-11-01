"use client";

import {
  DSAlert,
  DSButton,
  DSButtonLink,
  DSInput,
  DSStack,
  isEmail,
  useDSForm,
} from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { AuthCard } from "./components/auth-card/auth-card";
import { AuthLink } from "./components/auth-link/auth-link";
import { usePostForgotPassword } from "./hooks/mutations/use-post-forgot-password";
import { SIGN_IN_PATH } from "./typing/constants/auth-route.constant";
import type { ForgotPasswordValues } from "./typing/types/forgot-password-values.type";
import { toFormErrorText } from "./utils/form-error.util";

export const ForgotPasswordPage: FC = () => {
  const { t } = useTranslation("auth");
  const resolveMessage = useResolveApiErrorMessage();
  const forgotPassword = usePostForgotPassword();
  const form = useDSForm<ForgotPasswordValues>({
    mode: "controlled",
    initialValues: { email: "" },
    validate: { email: isEmail(t("errors.emailInvalid")) },
  });

  const handleValidSubmit = (values: ForgotPasswordValues): void => {
    forgotPassword.mutate({ email: values.email.trim() });
  };

  const handleEmailChange = (value: string): void => {
    form.setFieldValue("email", value);
  };

  if (forgotPassword.isSuccess) {
    return (
      <AuthCard title={t("forgotPassword.title")}>
        <DSStack gap={4}>
          <DSAlert color="success">
            {t("forgotPassword.sent", { email: forgotPassword.variables.email })}
          </DSAlert>
          <DSButtonLink href={SIGN_IN_PATH} type="primary" isFullWidth>
            {t("forgotPassword.backToSignIn")}
          </DSButtonLink>
        </DSStack>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title={t("forgotPassword.title")}
      description={t("forgotPassword.description")}
      footer={<AuthLink href={SIGN_IN_PATH}>{t("forgotPassword.backToSignIn")}</AuthLink>}
    >
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          {forgotPassword.error && (
            <DSAlert color="danger">{resolveMessage(forgotPassword.error)}</DSAlert>
          )}
          <DSInput
            type="email"
            label={t("forgotPassword.email")}
            value={form.values.email}
            onChange={handleEmailChange}
            error={toFormErrorText(form.errors.email)}
            autoComplete="email"
            isRequired
            isAutoFocused
          />
          <DSButton
            type="primary"
            nativeType="submit"
            isLoading={forgotPassword.isPending}
            isFullWidth
          >
            {t("forgotPassword.submit")}
          </DSButton>
        </DSStack>
      </form>
    </AuthCard>
  );
};
