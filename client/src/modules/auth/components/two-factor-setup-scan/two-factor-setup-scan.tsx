"use client";

import {
  DSAlert,
  DSButton,
  DSCode,
  DSPinInput,
  DSQrCode,
  DSStack,
  DSText,
} from "@/components/design-system";
import type { ApiError } from "@/lib/api/api-error";
import { useResolveApiErrorMessage } from "@/lib/api/hooks/use-resolve-api-error-message";
import { useRouter } from "next/navigation";
import { useState, type FC, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { usePostTwoFactorConfirm } from "../../hooks/mutations/use-post-two-factor-confirm";
import { QR_CODE_SIZE, TWO_FACTOR_CODE_LENGTH } from "../../typing/constants/auth-form.constant";
import { SignInReason } from "../../typing/enums/sign-in-reason.enum";
import type { TwoFactorSetupResponse } from "../../typing/types/auth-api.type";
import { buildSignInPath } from "../../utils/auth-path.util";
import styles from "./two-factor-setup-scan.module.scss";

interface Props {
  setup: TwoFactorSetupResponse;
  nextPath: string;
  onConfirmed: (recoveryCodes: readonly string[]) => void;
  onSetupExpired: () => void;
}

export const TwoFactorSetupScan: FC<Props> = ({ setup, nextPath, onConfirmed, onSetupExpired }) => {
  const { t } = useTranslation("auth");
  const router = useRouter();
  const resolveMessage = useResolveApiErrorMessage();
  const [code, setCode] = useState("");
  const [codeError, setCodeError] = useState<string | null>(null);
  const [alertMessage, setAlertMessage] = useState<string | null>(null);

  const handleConfirmError = (error: ApiError): void => {
    switch (error.code) {
      case "INVALID_TWO_FACTOR_CODE":
        setCode("");
        setCodeError(resolveMessage(error));
        return;
      case "NOT_SIGNED_IN":
        router.replace(buildSignInPath({ nextPath, reason: SignInReason.EXPIRED }));
        return;
      case "TWO_FACTOR_SETUP_NOT_STARTED":
        setCode("");
        onSetupExpired();
        return;
      default:
        setAlertMessage(resolveMessage(error));
    }
  };

  const confirmSetup = usePostTwoFactorConfirm({
    onSuccess: ({ recoveryCodes }) => {
      onConfirmed(recoveryCodes);
    },
    onError: handleConfirmError,
  });

  const submitCode = (value: string): void => {
    setCodeError(null);
    setAlertMessage(null);
    confirmSetup.mutate({ code: value });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    if (code.length < TWO_FACTOR_CODE_LENGTH) {
      setCodeError(t("errors.codeIncomplete"));
      return;
    }
    submitCode(code);
  };

  const handleCodeChange = (value: string): void => {
    setCode(value);
    setCodeError(null);
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <DSStack gap={4}>
        {alertMessage !== null && <DSAlert color="danger">{alertMessage}</DSAlert>}
        <div className={styles.qrCode}>
          <DSQrCode
            value={setup.setupUri}
            ariaLabel={t("twoFactorSetup.qrCodeLabel")}
            size={QR_CODE_SIZE}
          />
        </div>
        <DSStack gap={2}>
          <DSText size="sm" color="muted">
            {t("twoFactorSetup.manualKey")}
          </DSText>
          <DSCode isBlock isCopyable>
            {setup.key}
          </DSCode>
        </DSStack>
        <DSStack gap={2}>
          <DSText size="sm" weight="medium">
            {t("twoFactorSetup.codeLabel")}
          </DSText>
          <DSPinInput
            value={code}
            onChange={handleCodeChange}
            onComplete={submitCode}
            ariaLabel={t("twoFactorSetup.codeLabel")}
            length={TWO_FACTOR_CODE_LENGTH}
            hasError={codeError !== null}
            isDisabled={confirmSetup.isPending}
            isAutoFocused={false}
          />
          {codeError !== null && (
            <div role="alert">
              <DSText size="sm" color="danger">
                {codeError}
              </DSText>
            </div>
          )}
        </DSStack>
        <DSButton type="primary" nativeType="submit" isLoading={confirmSetup.isPending} isFullWidth>
          {t("twoFactorSetup.submit")}
        </DSButton>
      </DSStack>
    </form>
  );
};
