"use client";

import {
  DSAlert,
  DSButton,
  DSInput,
  DSPinInput,
  DSStack,
  DSText,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useRouter } from "next/navigation";
import { useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { AuthCard } from "./components/auth-card/auth-card";
import { AuthLink } from "./components/auth-link/auth-link";
import { AuthStepGate } from "./components/auth-step-gate/auth-step-gate";
import { usePostTwoFactor } from "./hooks/mutations/use-post-two-factor";
import { useAuthSearchParams } from "./hooks/use-auth-search-params";
import { useSignInStepRedirect } from "./hooks/use-sign-in-step-redirect";
import {
  RECOVERY_CODE_PLACEHOLDER,
  TWO_FACTOR_CODE_LENGTH,
} from "./typing/constants/auth-form.constant";
import { SIGN_IN_PATH } from "./typing/constants/auth-route.constant";
import { SignInReason } from "./typing/enums/sign-in-reason.enum";
import { buildSignInPath, buildSignInStepPath } from "./utils/auth-path.util";

export const TwoFactorPage: FC = () => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const { nextPath } = useAuthSearchParams();
  const { isReady, isLoadFailed, isRetrying, retry } = useSignInStepRedirect("two_factor_required");
  const [isRecoveryMode, setIsRecoveryMode] = useState(false);
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState<string | null>(null);
  const [alertMessage, setAlertMessage] = useState<string | null>(null);

  const handleVerifyError = (error: ApiError): void => {
    switch (error.code) {
      case "INVALID_TWO_FACTOR_CODE":
        setCode("");
        setCodeError(resolveMessage(error));
        return;
      case "NOT_SIGNED_IN":
        router.replace(buildSignInPath({ nextPath, reason: SignInReason.EXPIRED }));
        return;
      case "TWO_FACTOR_SETUP_NOT_STARTED":
        router.replace(buildSignInStepPath("two_factor_setup_required", nextPath));
        return;
      default:
        setAlertMessage(resolveMessage(error));
    }
  };

  const verify = usePostTwoFactor({
    onSuccess: () => {
      router.replace(nextPath);
    },
    onError: handleVerifyError,
  });

  const submitCode = (value: string): void => {
    setCodeError(null);
    setAlertMessage(null);
    verify.mutate({ code: value.trim() });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (!isRecoveryMode && code.length < TWO_FACTOR_CODE_LENGTH) {
      setCodeError(t("errors.codeIncomplete"));
      return;
    }
    if (isRecoveryMode && code.trim() === "") {
      setCodeError(t("errors.required"));
      return;
    }
    submitCode(code);
  };

  const handleCodeChange = (value: string): void => {
    setCode(value);
    setCodeError(null);
  };

  const handleModeToggle = (): void => {
    setIsRecoveryMode((isCurrentlyRecoveryMode) => {
      return !isCurrentlyRecoveryMode;
    });
    setCode("");
    setCodeError(null);
    setAlertMessage(null);
  };

  return (
    <AuthCard
      title={t("twoFactor.title")}
      description={isRecoveryMode ? t("twoFactor.recoveryDescription") : t("twoFactor.description")}
      footer={<AuthLink href={SIGN_IN_PATH}>{t("twoFactor.backToSignIn")}</AuthLink>}
    >
      <AuthStepGate
        isReady={isReady}
        isLoadFailed={isLoadFailed}
        isRetrying={isRetrying}
        onRetry={retry}
      >
        <form onSubmit={handleSubmit} noValidate>
          <DSStack gap={4}>
            {alertMessage !== null && <DSAlert color="danger">{alertMessage}</DSAlert>}
            {isRecoveryMode ? (
              <DSInput
                label={t("twoFactor.recoveryCodeLabel")}
                value={code}
                onChange={handleCodeChange}
                placeholder={RECOVERY_CODE_PLACEHOLDER}
                error={codeError ?? undefined}
                autoComplete="one-time-code"
                isDisabled={verify.isPending}
                isRequired
                isAutoFocused
              />
            ) : (
              <DSStack gap={2}>
                <DSPinInput
                  value={code}
                  onChange={handleCodeChange}
                  onComplete={submitCode}
                  ariaLabel={t("twoFactor.codeLabel")}
                  length={TWO_FACTOR_CODE_LENGTH}
                  hasError={codeError !== null}
                  isDisabled={verify.isPending}
                />
                {codeError !== null && (
                  <div role="alert">
                    <DSText size="sm" color="danger">
                      {codeError}
                    </DSText>
                  </div>
                )}
              </DSStack>
            )}
            <DSButton type="primary" nativeType="submit" isLoading={verify.isPending} isFullWidth>
              {t("twoFactor.submit")}
            </DSButton>
            <DSButton type="ghost" onClick={handleModeToggle}>
              {isRecoveryMode ? t("twoFactor.useAuthenticator") : t("twoFactor.useRecoveryCode")}
            </DSButton>
          </DSStack>
        </form>
      </AuthStepGate>
    </AuthCard>
  );
};
