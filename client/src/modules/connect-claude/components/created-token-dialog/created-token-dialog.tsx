"use client";

import { DSAlert, DSCode, DSModal, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLUGIN_MARKETPLACE_SOURCE } from "../../typing/constants/plugin.constant";
import type { CreatedApiToken } from "../../typing/types/api-token.type";
import { buildPluginInstallCommand } from "../../utils/plugin-install-command.util";

interface Props {
  createdToken: CreatedApiToken | null;
  onClose: () => void;
}

export const CreatedTokenDialog: FC<Props> = ({ createdToken, onClose }) => {
  const { t } = useTranslation("connectClaude");
  const isMarketplaceMissing = PLUGIN_MARKETPLACE_SOURCE === "";

  return (
    <DSModal
      isOpened={createdToken !== null}
      onClose={onClose}
      title={t("created.title", { projectKey: createdToken?.apiToken.projectKey ?? "" })}
      hasCancelButton={false}
      isClosedOnClickOutside={false}
      action={{ label: t("created.done"), onClick: onClose }}
    >
      {createdToken !== null && (
        <DSStack gap={4}>
          <DSAlert color="warning">{t("created.shownOnce")}</DSAlert>
          <DSStack gap={2}>
            <DSText size="sm" weight="medium">
              {t("created.commandLabel")}
            </DSText>
            <DSCode isBlock isCopyable>
              {buildPluginInstallCommand({
                marketplace: PLUGIN_MARKETPLACE_SOURCE,
                tessioUrl: window.location.origin,
                token: createdToken.token,
              })}
            </DSCode>
          </DSStack>
          {isMarketplaceMissing && (
            <DSAlert color="info">{t("created.marketplaceMissing")}</DSAlert>
          )}
          <DSText size="sm">{t("created.restart")}</DSText>
          <DSStack gap={2}>
            <DSText size="sm" weight="medium">
              {t("created.tokenLabel")}
            </DSText>
            <DSCode isBlock isCopyable>
              {createdToken.token}
            </DSCode>
          </DSStack>
        </DSStack>
      )}
    </DSModal>
  );
};
