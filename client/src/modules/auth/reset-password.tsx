"use client";

import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useRouter } from "next/navigation";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { AuthCard } from "./components/auth-card/auth-card";
import { InvalidLinkState } from "./components/invalid-link-state/invalid-link-state";
import { NewPasswordForm } from "./components/new-password-form/new-password-form";
import { usePostResetPassword } from "./hooks/mutations/use-post-reset-password";
import { FORGOT_PASSWORD_PATH } from "./typing/constants/auth-route.constant";
import { DEFAULT_NEXT_PATH } from "./typing/constants/session.constant";
import { SignInReason } from "./typing/enums/sign-in-reason.enum";
import { buildSignInPath } from "./utils/auth-path.util";

interface Props {
  token: string;
}

export const ResetPasswordPage: FC<Props> = ({ token }) => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const resetPassword = usePostResetPassword({
    onSuccess: () => {
      router.replace(
        buildSignInPath({ nextPath: DEFAULT_NEXT_PATH, reason: SignInReason.PASSWORD_RESET }),
      );
    },
  });
  const isInvalidLink = resetPassword.error?.code === "INVALID_ONE_TIME_LINK";
  const serverError =
    resetPassword.error && !isInvalidLink ? resolveMessage(resetPassword.error) : null;

  const handleSubmit = (password: string): void => {
    resetPassword.mutate({ token, password });
  };

  if (isInvalidLink) {
    return (
      <AuthCard title={t("resetPassword.title")}>
        <InvalidLinkState
          message={t("resetPassword.invalidLink")}
          href={FORGOT_PASSWORD_PATH}
          linkLabel={t("resetPassword.requestNewLink")}
        />
      </AuthCard>
    );
  }

  return (
    <AuthCard title={t("resetPassword.title")}>
      <NewPasswordForm
        submitLabel={t("resetPassword.submit")}
        isSubmitting={resetPassword.isPending || resetPassword.isSuccess}
        serverError={serverError}
        onSubmit={handleSubmit}
      />
    </AuthCard>
  );
};
