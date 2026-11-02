"use client";

import {
  DSAlert,
  DSBadge,
  DSButtonLink,
  DSCard,
  DSCode,
  DSEmptyState,
  DSErrorState,
  DSSkeleton,
  DSStack,
  DSTable,
  DSText,
} from "@/components/design-system";
import { useGetApiTokens } from "@/modules/connect-claude/hooks/queries/use-get-api-tokens";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLUGIN_STATE_BADGE_COLOR } from "../../typing/constants/plugin-state.constant";
import type { AiHarness } from "../../typing/types/ai-harness.type";
import { resolvePluginState } from "../../utils/plugin-version.util";
import styles from "./versions-card.module.scss";

const TOKEN_SKELETON_LINE_COUNT = 3;

interface Props {
  harness: AiHarness;
}

export const VersionsCard: FC<Props> = ({ harness }) => {
  const { t } = useTranslation("aiHarness");
  const formatDate = useFormatDate();
  const { data: tokens, isPending, isError, refetch, isRefetching } = useGetApiTokens();
  const activeTokens = (tokens ?? []).filter((token) => {
    return token.status === "active";
  });
  const tokenStates = activeTokens.map((token) => {
    return { token, state: resolvePluginState(token.pluginVersion, harness.plugin.version) };
  });
  const hasOutdatedPlugin = tokenStates.some(({ state }) => {
    return state === "outdated";
  });

  const handleRetry = (): void => {
    void refetch();
  };

  let tokenList = (
    <DSTable label={t("versions.yourPluginsLabel")}>
      <thead>
        <tr>
          <th scope="col">{t("versions.token")}</th>
          <th scope="col">{t("versions.project")}</th>
          <th scope="col">{t("versions.version")}</th>
          <th scope="col">{t("versions.lastUsed")}</th>
          <th scope="col">{t("versions.state")}</th>
        </tr>
      </thead>
      <tbody>
        {tokenStates.map(({ token, state }) => {
          return (
            <tr key={token.id}>
              <td>{token.name}</td>
              <td>{token.projectKey}</td>
              <td>
                {token.pluginVersion === null ? (
                  <span className={styles.muted}>{t("versions.notUsed")}</span>
                ) : (
                  <DSCode>{token.pluginVersion}</DSCode>
                )}
              </td>
              <td className={styles.muted}>
                {token.lastUsedAt === null ? t("versions.never") : formatDate(token.lastUsedAt)}
              </td>
              <td>
                <DSBadge color={PLUGIN_STATE_BADGE_COLOR[state]}>
                  {t(`pluginState.${state}`)}
                </DSBadge>
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
  if (isPending) {
    tokenList = <DSSkeleton lineCount={TOKEN_SKELETON_LINE_COUNT} />;
  } else if (isError) {
    tokenList = (
      <DSErrorState
        title={t("versions.tokensLoadFailed")}
        retryLabel={t("retry")}
        onRetry={handleRetry}
        isRetrying={isRefetching}
      />
    );
  } else if (activeTokens.length === 0) {
    tokenList = (
      <DSEmptyState
        title={t("versions.noTokens")}
        description={t("versions.noTokensHint")}
        icon="key"
        size="sm"
        titleOrder={3}
        action={
          <DSButtonLink href="/connect-claude" size="sm">
            {t("versions.connect")}
          </DSButtonLink>
        }
      />
    );
  }

  return (
    <DSCard title={t("versions.title")}>
      <DSStack gap={4}>
        <dl className={styles.versions}>
          <div className={styles.version}>
            <dt className={styles.versionLabel}>{t("versions.server")}</dt>
            <dd className={styles.versionValue}>{harness.server.version}</dd>
            {harness.server.buildCommit !== null && (
              <dd className={styles.muted}>
                {t("versions.commit", { commit: harness.server.buildCommit })}
              </dd>
            )}
          </div>
          <div className={styles.version}>
            <dt className={styles.versionLabel}>{t("versions.plugin")}</dt>
            <dd className={styles.versionValue}>{harness.plugin.version}</dd>
            <dd className={styles.muted}>{t("versions.pluginHint")}</dd>
          </div>
        </dl>
        <DSText weight="medium">{t("versions.yourPlugins")}</DSText>
        {tokenList}
        {hasOutdatedPlugin && (
          <DSAlert title={t("versions.updateTitle")} color="warning">
            <DSStack gap={2}>
              <DSText size="sm">{t("versions.updateHint")}</DSText>
              <DSCode isBlock isCopyable>
                {harness.plugin.updateCommand}
              </DSCode>
            </DSStack>
          </DSAlert>
        )}
      </DSStack>
    </DSCard>
  );
};
