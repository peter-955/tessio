"use client";

import {
  DSAlert,
  DSButton,
  DSInput,
  DSPasswordInput,
  DSStack,
  isEmail,
  isNotEmpty,
  useDSForm,
} from "@/components/design-system";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useRouter } from "next/navigation";
import { useEffect, type FC } from "react";
import { useTranslation } from "react-i18next";
import { AuthCard } from "./components/auth-card/auth-card";
import { AuthLink } from "./components/auth-link/auth-link";
import { usePostSignIn } from "./hooks/mutations/use-post-sign-in";
import { useGetCurrentUser } from "./hooks/queries/use-get-current-user";
import { useAuthSearchParams } from "./hooks/use-auth-search-params";
import { FORGOT_PASSWORD_PATH } from "./typing/constants/auth-route.constant";
import { SignInReason } from "./typing/enums/sign-in-reason.enum";
import type { SignInValues } from "./typing/types/sign-in-values.type";
import { buildSignInStepPath } from "./utils/auth-path.util";
import { toFormErrorText } from "./utils/form-error.util";

export const SignInPage: FC = () => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const { nextPath, reason } = useAuthSearchParams();
  const { data: currentUser } = useGetCurrentUser();
  const isSignedIn = currentUser?.nextStep === "signed_in";
  const signIn = usePostSignIn({
    onSuccess: ({ nextStep }) => {
      router.replace(buildSignInStepPath(nextStep, nextPath));
    },
  });
  const form = useDSForm<SignInValues>({
    mode: "controlled",
    initialValues: { email: "", password: "" },
    validate: {
      email: isEmail(t("errors.emailInvalid")),
      password: isNotEmpty(t("errors.required")),
    },
  });

  useEffect(() => {
    if (isSignedIn) {
      router.replace(nextPath);
    }
  }, [isSignedIn, nextPath, router]);

  const handleValidSubmit = (values: SignInValues): void => {
    signIn.mutate({ email: values.email.trim(), password: values.password });
  };

  const handleEmailChange = (value: string): void => {
    form.setFieldValue("email", value);
  };

  const handlePasswordChange = (value: string): void => {
    form.setFieldValue("password", value);
  };

  return (
    <AuthCard
      title={t("signIn.title")}
      footer={<AuthLink href={FORGOT_PASSWORD_PATH}>{t("signIn.forgotPassword")}</AuthLink>}
    >
      <form onSubmit={form.onSubmit(handleValidSubmit)} noValidate>
        <DSStack gap={4}>
          {reason === SignInReason.EXPIRED && (
            <DSAlert color="warning">{t("signIn.expired")}</DSAlert>
          )}
          {reason === SignInReason.PASSWORD_RESET && (
            <DSAlert color="success">{t("signIn.passwordReset")}</DSAlert>
          )}
          {signIn.error && <DSAlert color="danger">{resolveMessage(signIn.error)}</DSAlert>}
          <DSInput
            type="email"
            label={t("signIn.email")}
            value={form.values.email}
            onChange={handleEmailChange}
            error={toFormErrorText(form.errors.email)}
            autoComplete="email"
            isRequired
            isAutoFocused
          />
          <DSPasswordInput
            label={t("signIn.password")}
            value={form.values.password}
            onChange={handlePasswordChange}
            error={form.errors.password}
            autoComplete="current-password"
            isRequired
          />
          <DSButton type="primary" nativeType="submit" isLoading={signIn.isPending} isFullWidth>
            {t("signIn.submit")}
          </DSButton>
        </DSStack>
      </form>
    </AuthCard>
  );
};
