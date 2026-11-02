"use client";

import { DSCard, DSCode, DSEmptyState, DSTable } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { AiHarnessHook } from "../../typing/types/ai-harness.type";

interface Props {
  hooks: readonly AiHarnessHook[];
}

export const HooksCard: FC<Props> = ({ hooks }) => {
  const { t } = useTranslation("aiHarness");

  return (
    <DSCard title={t("hooks.title")}>
      {hooks.length === 0 ? (
        <DSEmptyState title={t("hooks.empty")} size="sm" titleOrder={3} />
      ) : (
        <DSTable label={t("hooks.label")}>
          <thead>
            <tr>
              <th scope="col">{t("hooks.event")}</th>
              <th scope="col">{t("hooks.tool")}</th>
              <th scope="col">{t("hooks.script")}</th>
              <th scope="col">{t("hooks.timeout")}</th>
            </tr>
          </thead>
          <tbody>
            {hooks.map((hook) => {
              return (
                <tr key={`${hook.event}-${hook.toolName ?? ""}-${hook.script}`}>
                  <td>{hook.event}</td>
                  <td>
                    {hook.toolName === null ? t("hooks.anyTool") : <DSCode>{hook.toolName}</DSCode>}
                  </td>
                  <td>
                    <DSCode>{hook.script}</DSCode>
                  </td>
                  <td>
                    {hook.timeoutSeconds === null
                      ? t("hooks.noTimeout")
                      : t("hooks.timeoutSeconds", { count: hook.timeoutSeconds })}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      )}
    </DSCard>
  );
};
