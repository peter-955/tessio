"use client";

import {
  DSActionIcon,
  DSBadge,
  DSCode,
  DSEmptyState,
  DSTable,
  DSText,
} from "@/components/design-system";
import { useFormatDate } from "@/shared/hooks/use-format-date";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { API_TOKEN_START } from "../../typing/constants/api-token.constant";
import { TOKEN_STATUS_BADGE_COLOR } from "../../typing/constants/token-status.constant";
import type { ApiToken } from "../../typing/types/api-token.type";
import styles from "./token-table.module.scss";

interface Props {
  tokens: readonly ApiToken[];
  onRevoke: (token: ApiToken) => void;
}

export const TokenTable: FC<Props> = ({ tokens, onRevoke }) => {
  const { t } = useTranslation("connectClaude");
  const formatDate = useFormatDate();

  if (tokens.length === 0) {
    return <DSEmptyState title={t("table.empty")} icon="key" size="sm" />;
  }

  return (
    <DSTable label={t("table.title")}>
      <thead>
        <tr>
          <th scope="col">{t("table.name")}</th>
          <th scope="col">{t("table.project")}</th>
          <th scope="col">{t("table.token")}</th>
          <th scope="col">{t("table.status")}</th>
          <th scope="col">{t("table.expires")}</th>
          <th scope="col">{t("table.lastUsed")}</th>
          <th scope="col">{t("table.created")}</th>
          <th scope="col">
            <span className={styles.visuallyHidden}>{t("table.actions")}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {tokens.map((token) => {
          const handleRevoke = (): void => {
            onRevoke(token);
          };

          return (
            <tr key={token.id}>
              <td>
                <DSText size="sm" weight="medium" component="span">
                  {token.name}
                </DSText>
              </td>
              <td>{token.projectKey}</td>
              <td>
                <DSCode>{`${API_TOKEN_START}${token.prefix}_…`}</DSCode>
              </td>
              <td>
                <DSBadge color={TOKEN_STATUS_BADGE_COLOR[token.status]}>
                  {t(`status.${token.status}`)}
                </DSBadge>
              </td>
              <td className={styles.muted}>{formatDate(token.expiresAt)}</td>
              <td className={styles.muted}>
                {token.lastUsedAt === null ? t("table.never") : formatDate(token.lastUsedAt)}
              </td>
              <td className={styles.muted}>{formatDate(token.createdAt)}</td>
              <td className={styles.actions}>
                {token.status === "active" && (
                  <DSActionIcon
                    icon="trash"
                    type="danger"
                    ariaLabel={t("table.revoke", { name: token.name })}
                    onClick={handleRevoke}
                  />
                )}
              </td>
            </tr>
          );
        })}
      </tbody>
    </DSTable>
  );
};
