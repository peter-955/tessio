"use client";

import { DSAlert, DSCode, DSModal, DSStack, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import { PLUGIN_INSTALL_PROTOCOL } from "../../typing/constants/plugin.constant";
import type { CreatedApiToken } from "../../typing/types/api-token.type";
import { buildJunitImportCommand } from "../../utils/junit-import-command.util";
import { buildPluginInstallCommand } from "../../utils/plugin-install-command.util";

interface Props {
  createdToken: CreatedApiToken | null;
  onClose: () => void;
}

export const CreatedTokenDialog: FC<Props> = ({ createdToken, onClose }) => {
  const { t } = useTranslation("connectClaude");
  const isInstallUnavailable = window.location.protocol !== PLUGIN_INSTALL_PROTOCOL;
  const isApiToken = createdToken?.apiToken.scope === "api";

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
          {isApiToken ? (
            <DSStack gap={2}>
              <DSText size="sm" weight="medium">
                {t("created.apiCommandLabel")}
              </DSText>
              <DSCode isBlock isCopyable>
                {buildJunitImportCommand({
                  tessioUrl: window.location.origin,
                  projectKey: createdToken.apiToken.projectKey,
                  token: createdToken.token,
                })}
              </DSCode>
              <DSText size="sm">{t("created.apiHint")}</DSText>
            </DSStack>
          ) : (
            <>
              <DSStack gap={2}>
                <DSText size="sm" weight="medium">
                  {t("created.commandLabel")}
                </DSText>
                <DSCode isBlock isCopyable>
                  {buildPluginInstallCommand({
                    tessioUrl: window.location.origin,
                    token: createdToken.token,
                  })}
                </DSCode>
              </DSStack>
              {isInstallUnavailable && <DSAlert color="info">{t("created.httpsOnly")}</DSAlert>}
              <DSText size="sm">{t("created.restart")}</DSText>
            </>
          )}
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
