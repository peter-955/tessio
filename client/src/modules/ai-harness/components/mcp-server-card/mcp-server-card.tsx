"use client";

import { DSCard, DSCode, DSEmptyState, DSStack, DSTable, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { AiHarnessMcpServer, AiHarnessMcpTool } from "../../typing/types/ai-harness.type";
import { RoleBadges } from "../role-badges/role-badges";

interface Props {
  servers: readonly AiHarnessMcpServer[];
  tools: readonly AiHarnessMcpTool[];
}

export const McpServerCard: FC<Props> = ({ servers, tools }) => {
  const { t } = useTranslation("aiHarness");

  if (servers.length === 0) {
    return (
      <DSCard title={t("mcp.title")}>
        <DSEmptyState title={t("mcp.empty")} size="sm" titleOrder={3} />
      </DSCard>
    );
  }

  return (
    <DSCard title={t("mcp.title")}>
      <DSStack gap={4}>
        <DSTable label={t("mcp.serversLabel")}>
          <thead>
            <tr>
              <th scope="col">{t("mcp.name")}</th>
              <th scope="col">{t("mcp.transport")}</th>
              <th scope="col">{t("mcp.url")}</th>
              <th scope="col">{t("mcp.headers")}</th>
            </tr>
          </thead>
          <tbody>
            {servers.map((server) => {
              return (
                <tr key={server.name}>
                  <td>{server.name}</td>
                  <td>{server.transport}</td>
                  <td>
                    <DSCode>{server.url}</DSCode>
                  </td>
                  <td>{server.headerNames.join(", ")}</td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
        <DSText weight="medium">{t("mcp.toolsTitle")}</DSText>
        <DSTable label={t("mcp.toolsLabel")}>
          <thead>
            <tr>
              <th scope="col">{t("mcp.tool")}</th>
              <th scope="col">{t("mcp.description")}</th>
              <th scope="col">{t("mcp.capability")}</th>
              <th scope="col">{t("mcp.roles")}</th>
            </tr>
          </thead>
          <tbody>
            {tools.map((tool) => {
              return (
                <tr key={tool.name}>
                  <td>
                    <DSCode>{tool.name}</DSCode>
                  </td>
                  <td>
                    <DSText size="sm" component="span">
                      {tool.description}
                    </DSText>
                  </td>
                  <td>
                    {tool.capability === null ? (
                      t("mcp.noCapability")
                    ) : (
                      <DSCode>{tool.capability}</DSCode>
                    )}
                  </td>
                  <td>
                    <RoleBadges roles={tool.roles} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </DSTable>
      </DSStack>
    </DSCard>
  );
};
