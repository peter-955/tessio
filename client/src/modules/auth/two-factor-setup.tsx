"use client";

import { DSErrorState, DSSkeleton, DSStack } from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { AuthCard } from "./components/auth-card/auth-card";
import { AuthStepGate } from "./components/auth-step-gate/auth-step-gate";
import { RecoveryCodes } from "./components/recovery-codes/recovery-codes";
import { TwoFactorSetupScan } from "./components/two-factor-setup-scan/two-factor-setup-scan";
import { usePostTwoFactorSetup } from "./hooks/mutations/use-post-two-factor-setup";
import { GET_CURRENT_USER_KEY } from "./hooks/queries/use-get-current-user";
import { useAuthSearchParams } from "./hooks/use-auth-search-params";
import { useSignInStepRedirect } from "./hooks/use-sign-in-step-redirect";
import { QR_CODE_SIZE } from "./typing/constants/auth-form.constant";
import { SignInReason } from "./typing/enums/sign-in-reason.enum";
import { buildSignInPath, buildSignInStepPath } from "./utils/auth-path.util";

const SKELETON_LINE_COUNT = 3;

export const TwoFactorSetupPage: FC = () => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const queryClient = useQueryClient();
  const { nextPath } = useAuthSearchParams();
  const [recoveryCodes, setRecoveryCodes] = useState<readonly string[] | null>(null);
  const hasStartedSetupRef = useRef(false);
  const { isReady, isLoadFailed, isRetrying, retry } = useSignInStepRedirect(
    "two_factor_setup_required",
    { isEnabled: recoveryCodes === null },
  );

  const handleStartError = (error: ApiError): void => {
    if (error.code === "TWO_FACTOR_ALREADY_SET_UP") {
      router.replace(buildSignInStepPath("two_factor_required", nextPath));
      return;
    }
    if (error.code === "NOT_SIGNED_IN") {
      router.replace(buildSignInPath({ nextPath, reason: SignInReason.EXPIRED }));
    }
  };

  const startSetup = usePostTwoFactorSetup({ onError: handleStartError });
  const { mutate: startSetupMutate } = startSetup;
  const isRedirectingAfterStartError =
    startSetup.error?.code === "TWO_FACTOR_ALREADY_SET_UP" ||
    startSetup.error?.code === "NOT_SIGNED_IN";

  useEffect(() => {
    if (!isReady || hasStartedSetupRef.current) {
      return;
    }
    hasStartedSetupRef.current = true;
    startSetupMutate();
  }, [isReady, startSetupMutate]);

  const handleRetryStart = (): void => {
    startSetup.mutate();
  };

  const handleContinue = (): void => {
    queryClient.removeQueries({ queryKey: [GET_CURRENT_USER_KEY] });
    router.replace(nextPath);
  };

  if (recoveryCodes !== null) {
    return (
      <AuthCard title={t("twoFactorSetup.title")}>
        <RecoveryCodes codes={recoveryCodes} onContinue={handleContinue} />
      </AuthCard>
    );
  }

  let setupStep: ReactNode = (
    <DSStack gap={4} align="center">
      <DSSkeleton height={QR_CODE_SIZE} width={QR_CODE_SIZE} radius="md" />
      <DSSkeleton lineCount={SKELETON_LINE_COUNT} width="100%" />
    </DSStack>
  );
  if (startSetup.data) {
    setupStep = (
      <TwoFactorSetupScan
        setup={startSetup.data}
        nextPath={nextPath}
        onConfirmed={setRecoveryCodes}
        onSetupExpired={handleRetryStart}
      />
    );
  } else if (startSetup.isError && !isRedirectingAfterStartError) {
    setupStep = (
      <DSErrorState
        title={t("twoFactorSetup.startFailed")}
        retryLabel={t("twoFactorSetup.retry")}
        onRetry={handleRetryStart}
      />
    );
  }

  return (
    <AuthCard title={t("twoFactorSetup.title")} description={t("twoFactorSetup.description")}>
      <AuthStepGate
        isReady={isReady}
        isLoadFailed={isLoadFailed}
        isRetrying={isRetrying}
        onRetry={retry}
      >
        {setupStep}
      </AuthStepGate>
    </AuthCard>
  );
};
