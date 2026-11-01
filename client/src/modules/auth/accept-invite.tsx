"use client";

import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useRouter } from "next/navigation";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { AuthCard } from "./components/auth-card/auth-card";
import { InvalidLinkState } from "./components/invalid-link-state/invalid-link-state";
import { NewPasswordForm } from "./components/new-password-form/new-password-form";
import { usePostAcceptInvite } from "./hooks/mutations/use-post-accept-invite";
import { SIGN_IN_PATH } from "./typing/constants/auth-route.constant";
import { DEFAULT_NEXT_PATH } from "./typing/constants/session.constant";
import { buildSignInStepPath } from "./utils/auth-path.util";

interface Props {
  token: string;
}

export const AcceptInvitePage: FC<Props> = ({ token }) => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const acceptInvite = usePostAcceptInvite({
    onSuccess: ({ nextStep }) => {
      router.replace(buildSignInStepPath(nextStep, DEFAULT_NEXT_PATH));
    },
  });
  const isInvalidLink = acceptInvite.error?.code === "INVALID_ONE_TIME_LINK";
  const serverError =
    acceptInvite.error && !isInvalidLink ? resolveMessage(acceptInvite.error) : null;

  const handleSubmit = (password: string): void => {
    acceptInvite.mutate({ token, password });
  };

  if (isInvalidLink) {
    return (
      <AuthCard title={t("acceptInvite.title")}>
        <InvalidLinkState
          message={t("acceptInvite.invalidLink")}
          href={SIGN_IN_PATH}
          linkLabel={t("acceptInvite.goToSignIn")}
        />
      </AuthCard>
    );
  }

  return (
    <AuthCard title={t("acceptInvite.title")} description={t("acceptInvite.description")}>
      <NewPasswordForm
        submitLabel={t("acceptInvite.submit")}
        isSubmitting={acceptInvite.isPending || acceptInvite.isSuccess}
        serverError={serverError}
        onSubmit={handleSubmit}
      />
    </AuthCard>
  );
};
