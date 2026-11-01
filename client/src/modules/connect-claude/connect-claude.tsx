"use client";

import {
  DSCard,
  DSErrorState,
  DSPageHeader,
  DSSkeleton,
  DSStack,
  DSText,
} from "@/components/design-system";
import { useState, type FC } from "react";
import { useTranslation } from "react-i18next";
import { CreateTokenForm } from "./components/create-token-form/create-token-form";
import { RevokeTokenConfirm } from "./components/revoke-token-confirm/revoke-token-confirm";
import { TokenTable } from "./components/token-table/token-table";
import styles from "./connect-claude.module.scss";
import { useGetApiTokens } from "./hooks/queries/use-get-api-tokens";
import { MAX_ACTIVE_API_TOKENS } from "./typing/constants/api-token.constant";
import type { ApiToken } from "./typing/types/api-token.type";
import { countActiveTokens } from "./utils/token-status.util";

const TABLE_SKELETON_LINE_COUNT = 4;

export const ConnectClaudePage: FC = () => {
  const { t } = useTranslation("connectClaude");
  const { data: tokens, isPending, isError, refetch, isRefetching } = useGetApiTokens();
  const [tokenToRevoke, setTokenToRevoke] = useState<ApiToken | null>(null);
  const activeTokenCount = tokens === undefined ? 0 : countActiveTokens(tokens);

  const handleRetry = (): void => {
    void refetch();
  };

  const handleCloseRevoke = (): void => {
    setTokenToRevoke(null);
  };

  let tokenList = <TokenTable tokens={tokens ?? []} onRevoke={setTokenToRevoke} />;
  if (isPending) {
    tokenList = <DSSkeleton lineCount={TABLE_SKELETON_LINE_COUNT} />;
  } else if (isError) {
    tokenList = (
      <DSErrorState
        title={t("table.loadFailed")}
        retryLabel={t("table.retry")}
        onRetry={handleRetry}
        isRetrying={isRefetching}
      />
    );
  }

  return (
    <>
      <DSPageHeader title={t("title")} description={t("description")} />
      <DSStack gap={5} className={styles.content}>
        <ol className={styles.steps} aria-label={t("steps.label")}>
          <li>{t("steps.create")}</li>
          <li>{t("steps.install")}</li>
          <li>{t("steps.restart")}</li>
        </ol>
        <CreateTokenForm activeTokenCount={activeTokenCount} />
        <DSCard title={t("table.title")}>
          <DSStack gap={3}>
            {tokens !== undefined && (
              <DSText size="sm" color="muted">
                {t("table.activeCount", { count: activeTokenCount, max: MAX_ACTIVE_API_TOKENS })}
              </DSText>
            )}
            {tokenList}
          </DSStack>
        </DSCard>
      </DSStack>
      <RevokeTokenConfirm token={tokenToRevoke} onClose={handleCloseRevoke} />
    </>
  );
};
