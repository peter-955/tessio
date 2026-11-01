import type { ApiToken } from "../typing/types/api-token.type";

export const countActiveTokens = (tokens: readonly ApiToken[]): number => {
  return tokens.filter((token) => {
    return token.status === "active";
  }).length;
};
