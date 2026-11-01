"use client";

import { DSErrorState, DSLoader } from "@/components/design-system";
import {
  GET_CURRENT_USER_KEY,
  useGetCurrentUser,
} from "@/modules/auth/hooks/queries/use-get-current-user";
import { UNAUTHORIZED_STATUS } from "@/modules/auth/typing/constants/http-status.constant";
import { SignInReason } from "@/modules/auth/typing/enums/sign-in-reason.enum";
import {
  buildCurrentPath,
  buildSignInPath,
  buildSignInStepPath,
} from "@/modules/auth/utils/auth-path.util";
import { useLiveEvents } from "@/shared/hooks/use-live-events";
import { useQueryClient } from "@tanstack/react-query";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, type FC, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useRefetchCurrentUserOnUnauthorized } from "./hooks/use-refetch-current-user-on-unauthorized";
import { SessionGuardContext } from "./session-guard.context";
import styles from "./session-guard.module.scss";

interface Props {
  children: ReactNode;
}

export const SessionGuard: FC<Props> = ({ children }) => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { data: currentUser, error, refetch, isRefetching } = useGetCurrentUser();
  const currentPath = buildCurrentPath(pathname, searchParams.toString());
  const isUnauthorized = error?.status === UNAUTHORIZED_STATUS;
  const currentStep = isUnauthorized ? undefined : currentUser?.nextStep;
  const isSignedIn = currentStep === "signed_in";

  useRefetchCurrentUserOnUnauthorized();

  const handleStreamClosed = useCallback((): void => {
    void queryClient.invalidateQueries({ queryKey: [GET_CURRENT_USER_KEY] });
  }, [queryClient]);

  useLiveEvents({ isEnabled: isSignedIn, onStreamClosed: handleStreamClosed });

  useEffect(() => {
    if (isUnauthorized) {
      router.replace(buildSignInPath({ nextPath: currentPath, reason: SignInReason.EXPIRED }));
      return;
    }
    if (currentStep !== undefined && currentStep !== "signed_in") {
      router.replace(buildSignInStepPath(currentStep, currentPath));
    }
  }, [currentPath, currentStep, isUnauthorized, router]);

  const handleRetry = (): void => {
    void refetch();
  };

  if (currentUser !== undefined && isSignedIn) {
    return <SessionGuardContext value={currentUser}>{children}</SessionGuardContext>;
  }

  if (error !== null && !isUnauthorized && currentUser === undefined) {
    return (
      <div className={styles.screen}>
        <DSErrorState
          title={t("session.loadFailed")}
          retryLabel={t("session.retry")}
          onRetry={handleRetry}
          isRetrying={isRefetching}
        />
      </div>
    );
  }

  return (
    <div className={styles.screen}>
      <DSLoader size="md" />
    </div>
  );
};
