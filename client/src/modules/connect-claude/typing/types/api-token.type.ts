import type { components } from "@/lib/api/openapi.type";
import type { TOKEN_LIFETIME_DAYS } from "../constants/api-token.constant";

export type ApiToken = components["schemas"]["ApiTokenResponse"];

export type CreatedApiToken = components["schemas"]["CreatedApiTokenResponse"];

export type ApiTokenStatus = components["schemas"]["ApiTokenStatus"];

export type CreateApiTokenRequest = components["schemas"]["CreateApiTokenRequest"];

export type TokenLifetime = (typeof TOKEN_LIFETIME_DAYS)[number];

export interface CreateApiTokenValues {
  name: string;
  projectKey: string | null;
  lifetimeDays: TokenLifetime;
}
