import { readFileSync } from "node:fs";
import { expect, type APIRequestContext } from "@playwright/test";
import { E2E_PATHS } from "../constants/e2e-environment.constant.ts";
import type { CreatedApiToken, McpToolCallResponse } from "../types/mcp-tool.type.ts";

const readPluginVersion = (): string => {
  const manifest: { version: string } = JSON.parse(readFileSync(E2E_PATHS.pluginManifest, "utf8"));
  return manifest.version;
};

export const createApiToken = async (
  request: APIRequestContext,
  projectKey: string,
  name: string,
): Promise<CreatedApiToken> => {
  const response = await request.post("/api/me/api-tokens", { data: { name, projectKey } });
  expect(response.status()).toBe(201);
  const createdToken: CreatedApiToken = await response.json();
  return createdToken;
};

export const revokeApiToken = async (
  request: APIRequestContext,
  tokenId: string,
): Promise<void> => {
  const response = await request.delete(`/api/me/api-tokens/${tokenId}`);
  expect(response.status()).toBe(204);
};

export const callTessioTool = async <Reply>(
  request: APIRequestContext,
  token: string,
  name: string,
  toolArguments: Record<string, unknown>,
): Promise<Reply> => {
  const response = await request.post("/mcp", {
    headers: {
      accept: "application/json, text/event-stream",
      authorization: `Bearer ${token}`,
      "x-tessio-plugin-version": readPluginVersion(),
    },
    data: {
      jsonrpc: "2.0",
      id: 1,
      method: "tools/call",
      params: { name, arguments: toolArguments },
    },
  });
  expect(response.ok()).toBe(true);
  const body: McpToolCallResponse = await response.json();
  const text = body.result?.content[0]?.text;
  if (body.result === undefined || body.result.isError === true || text === undefined) {
    throw new Error(`The ${name} tool failed: ${JSON.stringify(body)}`);
  }
  const reply: Reply = JSON.parse(text);
  return reply;
};
